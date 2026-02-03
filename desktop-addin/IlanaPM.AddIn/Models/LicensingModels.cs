using System;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Request to activate a license key
    /// </summary>
    public class ActivationRequest
    {
        public string license_key { get; set; }
        public string user_email { get; set; }
        public string device_id { get; set; }
    }

    /// <summary>
    /// Response from license activation
    /// </summary>
    public class ActivationResponse
    {
        public string activation_token { get; set; }
        public string user_id { get; set; }
        public string org_id { get; set; }
        public string org_name { get; set; }
        public string tier { get; set; }
        public int seats_used { get; set; }
        public int seats_purchased { get; set; }
        public string subscription_end { get; set; }
        public string message { get; set; }
    }

    /// <summary>
    /// License information for display in settings
    /// </summary>
    public class LicenseInfo
    {
        public string user_email { get; set; }
        public string org_id { get; set; }
        public string org_name { get; set; }
        public string tier { get; set; }
        public int seats_used { get; set; }
        public int seats_purchased { get; set; }
        public string subscription_start { get; set; }
        public string subscription_end { get; set; }
        public string status { get; set; }
        public bool sso_enabled { get; set; }
    }

    /// <summary>
    /// Billing portal URL response
    /// </summary>
    public class BillingPortalResponse
    {
        public string portal_url { get; set; }
    }

    /// <summary>
    /// Custom exception for license-related errors
    /// </summary>
    public class LicenseException : Exception
    {
        public LicenseException(string message) : base(message) { }
        public LicenseException(string message, Exception innerException) : base(message, innerException) { }
    }

    /// <summary>
    /// Exception thrown when license is expired or invalid
    /// </summary>
    public class LicenseExpiredException : LicenseException
    {
        public LicenseExpiredException(string message) : base(message) { }
    }

    /// <summary>
    /// Exception thrown when API returns 401 Unauthorized
    /// </summary>
    public class UnauthorizedException : LicenseException
    {
        public UnauthorizedException(string message) : base(message) { }
    }
}
