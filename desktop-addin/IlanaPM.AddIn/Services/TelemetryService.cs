using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using IlanaPM.AddIn.Models;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Telemetry service for ML learning and usage analytics
    /// Privacy-focused: Opt-in consent, anonymized user IDs, no PII collection
    /// </summary>
    public class TelemetryService
    {
        private Queue<TelemetryEvent> eventQueue;
        private string sessionId;
        private bool userConsented;
        private DateTime sessionStartTime;
        private const int BATCH_SIZE = 10;  // Send batch when queue reaches this size

        /// <summary>
        /// Initialize telemetry service
        /// </summary>
        public TelemetryService()
        {
            sessionId = Guid.NewGuid().ToString();
            sessionStartTime = DateTime.UtcNow;
            eventQueue = new Queue<TelemetryEvent>();
            LoadUserConsent();

            // Note: Session tracking moved to ThisAddIn for consistency
        }

        /// <summary>
        /// Track a telemetry event
        /// </summary>
        public void TrackEvent(TelemetryEventType type, Dictionary<string, object> properties = null)
        {
            if (!userConsented)
            {
                System.Diagnostics.Debug.WriteLine($"Telemetry: User has not consented - event {type} not tracked");
                return;
            }

            try
            {
                var telemetryEvent = new TelemetryEvent(type)
                {
                    session_id = sessionId,
                    user_id = GetHashedUserId(),
                    user_consented = true
                };

                // Add properties if provided
                if (properties != null)
                {
                    foreach (var kvp in properties)
                    {
                        telemetryEvent.AddProperty(kvp.Key, kvp.Value);
                    }
                }

                eventQueue.Enqueue(telemetryEvent);

                System.Diagnostics.Debug.WriteLine($"Telemetry: Tracked {type} event (queue size: {eventQueue.Count})");

                // Auto-flush if batch size reached
                if (eventQueue.Count >= BATCH_SIZE)
                {
                    FlushEventsAsync();
                }
            }
            catch (Exception ex)
            {
                // Telemetry should never break user experience
                System.Diagnostics.Debug.WriteLine($"Telemetry tracking error: {ex.Message}");
            }
        }

        /// <summary>
        /// Send queued events to API (async)
        /// </summary>
        public async void FlushEventsAsync()
        {
            if (eventQueue.Count == 0)
            {
                return;
            }

            try
            {
                // Dequeue all events into batch
                var batch = new TelemetryBatch();
                while (eventQueue.Count > 0)
                {
                    batch.events.Add(eventQueue.Dequeue());
                }

                System.Diagnostics.Debug.WriteLine($"Telemetry: Flushing {batch.events.Count} events to API");

                // Send to backend API
                var apiClient = new ApiClient();
                await apiClient.SendTelemetryBatchAsync(batch);

                System.Diagnostics.Debug.WriteLine($"Telemetry: Successfully sent {batch.events.Count} events");
            }
            catch (Exception ex)
            {
                // Fail silently - telemetry should never break user experience
                System.Diagnostics.Debug.WriteLine($"Telemetry send failed: {ex.Message}");
                // Note: Events are lost on failure (by design - don't want to accumulate forever)
            }
        }

        /// <summary>
        /// Flush events synchronously (for app shutdown)
        /// </summary>
        public void FlushEventsSync()
        {
            if (eventQueue.Count == 0)
            {
                return;
            }

            try
            {
                // Send synchronously (blocking)
                // Note: SessionEnded should already be tracked by caller (ThisAddIn_Shutdown)
                FlushEventsAsync();
                System.Threading.Thread.Sleep(1000); // Give it a second to send
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Telemetry flush on shutdown failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Get session duration in seconds
        /// </summary>
        public double GetSessionDurationSeconds()
        {
            return (DateTime.UtcNow - sessionStartTime).TotalSeconds;
        }

        /// <summary>
        /// Hash user email for privacy (SHA-256)
        /// Irreversible - cannot recover email from hash
        /// </summary>
        private string GetHashedUserId()
        {
            try
            {
                string email = SecureStorage.ReadUserEmail();
                if (string.IsNullOrEmpty(email))
                {
                    return "anonymous";
                }

                using (SHA256 sha256 = SHA256.Create())
                {
                    byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(email));
                    return Convert.ToBase64String(bytes);
                }
            }
            catch
            {
                return "anonymous";
            }
        }

        /// <summary>
        /// Load user consent from settings
        /// </summary>
        private void LoadUserConsent()
        {
            try
            {
                // Check if user has consented to telemetry
                // Default is FALSE (opt-in, not opt-out)
                userConsented = Properties.Settings.Default.TelemetryConsent;
                System.Diagnostics.Debug.WriteLine($"Telemetry: User consent = {userConsented}");
            }
            catch
            {
                userConsented = false;
            }
        }

        /// <summary>
        /// Set user consent (called from Settings form)
        /// </summary>
        public void SetUserConsent(bool consent)
        {
            userConsented = consent;
            Properties.Settings.Default.TelemetryConsent = consent;
            Properties.Settings.Default.Save();

            System.Diagnostics.Debug.WriteLine($"Telemetry: User consent updated to {consent}");

            // If user opted out, clear queue (don't send events without consent)
            if (!consent)
            {
                eventQueue.Clear();
            }
            // If user just opted in, queue starts fresh (don't retroactively track session start)
        }

        /// <summary>
        /// Get current consent status
        /// </summary>
        public bool HasUserConsent()
        {
            return userConsented;
        }

        /// <summary>
        /// Get current queue size (for debugging)
        /// </summary>
        public int GetQueueSize()
        {
            return eventQueue.Count;
        }

        /// <summary>
        /// Track feature sequence (common workflow pattern)
        /// Example: Template → Validate → Critical Path
        /// </summary>
        public void TrackFeatureSequence(string[] features)
        {
            if (!userConsented || features == null || features.Length == 0)
            {
                return;
            }

            TrackEvent(TelemetryEventType.FeatureSequence, new Dictionary<string, object>
            {
                { "sequence", string.Join(" → ", features) },
                { "feature_count", features.Length }
            });
        }
    }
}
