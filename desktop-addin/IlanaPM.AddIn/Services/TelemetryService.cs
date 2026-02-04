using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Timers;
using IlanaPM.AddIn.Models;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Telemetry service for ML feedback loop
    /// Tracks user actions and project data to improve duration predictions and timeline recommendations
    /// Privacy-focused: User IDs are hashed, no PII is collected
    /// </summary>
    public class TelemetryService : IDisposable
    {
        private readonly ApiClient apiClient;
        private readonly List<TelemetryEvent> eventQueue;
        private readonly Timer batchTimer;
        private readonly string hashedUserId;
        private readonly MSProject.Application msProjectApp;

        private const int BATCH_INTERVAL_MS = 60000; // Send batch every 60 seconds
        private const int MAX_BATCH_SIZE = 50; // Max events per batch

        public TelemetryService(MSProject.Application app)
        {
            this.msProjectApp = app;
            this.apiClient = new ApiClient();
            this.eventQueue = new List<TelemetryEvent>();

            // Generate hashed user ID (privacy-focused: no reversible PII)
            this.hashedUserId = GenerateHashedUserId();

            // Set up batch timer for periodic sending
            this.batchTimer = new Timer(BATCH_INTERVAL_MS);
            this.batchTimer.Elapsed += OnBatchTimerElapsed;
            this.batchTimer.Start();

            System.Diagnostics.Debug.WriteLine($"TelemetryService initialized for hashed user: {hashedUserId.Substring(0, 8)}...");
        }

        /// <summary>
        /// Generate hashed user ID from machine name and user name
        /// Cannot be reversed to identify individual users (privacy-focused)
        /// </summary>
        private string GenerateHashedUserId()
        {
            string uniqueString = $"{Environment.MachineName}|{Environment.UserName}";
            using (var sha256 = SHA256.Create())
            {
                byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(uniqueString));
                return Convert.ToBase64String(hashBytes).Substring(0, 16); // 16 chars is sufficient
            }
        }

        /// <summary>
        /// Track a user action event
        /// </summary>
        public void TrackEvent(TelemetryEventType eventType, Dictionary<string, object> properties = null)
        {
            try
            {
                var telemetryEvent = new TelemetryEvent
                {
                    event_type = eventType.ToString(),
                    timestamp = DateTime.UtcNow,
                    user_id = hashedUserId,
                    properties = properties ?? new Dictionary<string, object>()
                };

                lock (eventQueue)
                {
                    eventQueue.Add(telemetryEvent);

                    // Send immediately if batch is full
                    if (eventQueue.Count >= MAX_BATCH_SIZE)
                    {
                        SendBatch();
                    }
                }
            }
            catch (Exception ex)
            {
                // Never let telemetry errors affect user experience
                System.Diagnostics.Debug.WriteLine($"Telemetry error (event): {ex.Message}");
            }
        }

        /// <summary>
        /// Track task completion for ML learning
        /// Compares actual vs estimated duration
        /// </summary>
        public void TrackTaskCompletion(MSProject.Task task)
        {
            try
            {
                var properties = new Dictionary<string, object>
                {
                    { "task_name", task.Name },
                    { "estimated_duration_days", task.Duration / 480.0 }, // Convert minutes to days
                    { "actual_duration_days", task.ActualDuration / 480.0 },
                    { "variance_days", (task.ActualDuration - task.Duration) / 480.0 },
                    { "category", task.GetField(MSProject.PjField.pjTaskText4) ?? "" },
                    { "phase", task.GetField(MSProject.PjField.pjTaskText12) ?? "" },
                    { "country", task.GetField(MSProject.PjField.pjTaskText11) ?? "" }
                };

                TrackEvent(TelemetryEventType.TaskCompleted, properties);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Telemetry error (task completion): {ex.Message}");
            }
        }

        /// <summary>
        /// Track project metadata for ML context
        /// </summary>
        public void TrackProjectMetadata(ClinicalProjectConfiguration config)
        {
            try
            {
                var properties = new Dictionary<string, object>
                {
                    { "study_phase", config.StudyPhase },
                    { "therapeutic_area", config.TherapeuticArea },
                    { "country_count", config.Countries?.Count ?? 0 },
                    { "site_count", config.Sites?.Count ?? 0 },
                    { "cohort_count", config.Cohorts?.Count ?? 0 }
                };

                TrackEvent(TelemetryEventType.ProjectOpened, properties);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Telemetry error (project metadata): {ex.Message}");
            }
        }

        /// <summary>
        /// Periodic batch send timer
        /// </summary>
        private void OnBatchTimerElapsed(object sender, ElapsedEventArgs e)
        {
            SendBatch();
        }

        /// <summary>
        /// Send queued events to backend as batch
        /// </summary>
        private void SendBatch()
        {
            try
            {
                List<TelemetryEvent> eventsToSend;

                lock (eventQueue)
                {
                    if (eventQueue.Count == 0)
                        return;

                    // Take all events from queue
                    eventsToSend = new List<TelemetryEvent>(eventQueue);
                    eventQueue.Clear();
                }

                // Create batch
                var batch = new TelemetryBatch
                {
                    events = eventsToSend
                };

                // Send asynchronously (fire and forget - don't block user)
                apiClient.SendTelemetryBatchAsync(batch).ContinueWith(task =>
                {
                    if (task.Exception != null)
                    {
                        System.Diagnostics.Debug.WriteLine($"Telemetry batch send error: {task.Exception.InnerException?.Message}");
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine($"Telemetry batch sent: {eventsToSend.Count} events");
                    }
                });
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Telemetry error (send batch): {ex.Message}");
            }
        }

        /// <summary>
        /// Dispose and send remaining events
        /// </summary>
        public void Dispose()
        {
            try
            {
                batchTimer?.Stop();
                batchTimer?.Dispose();

                // Send any remaining events
                SendBatch();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Telemetry error (dispose): {ex.Message}");
            }
        }
    }
}
