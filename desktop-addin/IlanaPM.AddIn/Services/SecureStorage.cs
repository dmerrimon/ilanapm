using System;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Secure storage for JWT activation token using Windows DPAPI encryption
    /// Token is stored in Windows registry encrypted per-user
    /// </summary>
    public static class SecureStorage
    {
        private const string REGISTRY_KEY_PATH = @"Software\IlanaPM";
        private const string TOKEN_VALUE_NAME = "ActivationToken";
        private const string EMAIL_VALUE_NAME = "UserEmail";
        private const string ORG_ID_VALUE_NAME = "OrgId";
        private const string TIER_VALUE_NAME = "Tier";

        /// <summary>
        /// Save encrypted activation token to Windows registry
        /// Uses DPAPI (Data Protection API) for CurrentUser scope encryption
        /// </summary>
        public static void SaveToken(string token)
        {
            try
            {
                if (string.IsNullOrEmpty(token))
                {
                    throw new ArgumentException("Token cannot be null or empty", nameof(token));
                }

                // Encrypt token using DPAPI
                byte[] tokenBytes = Encoding.UTF8.GetBytes(token);
                byte[] encryptedBytes = ProtectedData.Protect(
                    tokenBytes,
                    null, // No additional entropy
                    DataProtectionScope.CurrentUser // Only current Windows user can decrypt
                );

                // Convert to Base64 for registry storage
                string encryptedToken = Convert.ToBase64String(encryptedBytes);

                // Store in registry
                using (RegistryKey key = Registry.CurrentUser.CreateSubKey(REGISTRY_KEY_PATH))
                {
                    if (key != null)
                    {
                        key.SetValue(TOKEN_VALUE_NAME, encryptedToken, RegistryValueKind.String);
                        System.Diagnostics.Debug.WriteLine("Token saved successfully to registry");
                    }
                    else
                    {
                        throw new Exception("Failed to create registry key");
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving token: {ex.Message}");
                throw new Exception($"Failed to save activation token: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Read and decrypt activation token from Windows registry
        /// Returns null if no token exists
        /// </summary>
        public static string ReadToken()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(REGISTRY_KEY_PATH))
                {
                    if (key == null)
                    {
                        System.Diagnostics.Debug.WriteLine("Registry key does not exist - no token stored");
                        return null;
                    }

                    string encryptedToken = key.GetValue(TOKEN_VALUE_NAME) as string;
                    if (string.IsNullOrEmpty(encryptedToken))
                    {
                        System.Diagnostics.Debug.WriteLine("No token found in registry");
                        return null;
                    }

                    // Decrypt token using DPAPI
                    byte[] encryptedBytes = Convert.FromBase64String(encryptedToken);
                    byte[] decryptedBytes = ProtectedData.Unprotect(
                        encryptedBytes,
                        null,
                        DataProtectionScope.CurrentUser
                    );

                    string token = Encoding.UTF8.GetString(decryptedBytes);
                    System.Diagnostics.Debug.WriteLine("Token read successfully from registry");
                    return token;
                }
            }
            catch (CryptographicException ex)
            {
                System.Diagnostics.Debug.WriteLine($"Token decryption failed (corrupted or from different user): {ex.Message}");
                // Token might be corrupted or from different Windows user
                // Clear it and return null
                ClearToken();
                return null;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error reading token: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Save user email (not encrypted - just for display purposes)
        /// </summary>
        public static void SaveUserEmail(string email)
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.CreateSubKey(REGISTRY_KEY_PATH))
                {
                    if (key != null)
                    {
                        key.SetValue(EMAIL_VALUE_NAME, email ?? "", RegistryValueKind.String);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving user email: {ex.Message}");
            }
        }

        /// <summary>
        /// Read user email from registry
        /// </summary>
        public static string ReadUserEmail()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(REGISTRY_KEY_PATH))
                {
                    if (key == null) return null;
                    return key.GetValue(EMAIL_VALUE_NAME) as string;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error reading user email: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Save organization ID (for display purposes)
        /// </summary>
        public static void SaveOrgId(string orgId)
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.CreateSubKey(REGISTRY_KEY_PATH))
                {
                    if (key != null)
                    {
                        key.SetValue(ORG_ID_VALUE_NAME, orgId ?? "", RegistryValueKind.String);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving org ID: {ex.Message}");
            }
        }

        /// <summary>
        /// Read organization ID from registry
        /// </summary>
        public static string ReadOrgId()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(REGISTRY_KEY_PATH))
                {
                    if (key == null) return null;
                    return key.GetValue(ORG_ID_VALUE_NAME) as string;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error reading org ID: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Save tier (professional/enterprise)
        /// </summary>
        public static void SaveTier(string tier)
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.CreateSubKey(REGISTRY_KEY_PATH))
                {
                    if (key != null)
                    {
                        key.SetValue(TIER_VALUE_NAME, tier ?? "", RegistryValueKind.String);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving tier: {ex.Message}");
            }
        }

        /// <summary>
        /// Read tier from registry
        /// </summary>
        public static string ReadTier()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(REGISTRY_KEY_PATH))
                {
                    if (key == null) return null;
                    return key.GetValue(TIER_VALUE_NAME) as string;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error reading tier: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Clear all stored license data from registry
        /// Used when token expires or user deactivates
        /// </summary>
        public static void ClearToken()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(REGISTRY_KEY_PATH, true))
                {
                    if (key != null)
                    {
                        key.DeleteValue(TOKEN_VALUE_NAME, false);
                        key.DeleteValue(EMAIL_VALUE_NAME, false);
                        key.DeleteValue(ORG_ID_VALUE_NAME, false);
                        key.DeleteValue(TIER_VALUE_NAME, false);
                        System.Diagnostics.Debug.WriteLine("License data cleared from registry");
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error clearing token: {ex.Message}");
            }
        }

        /// <summary>
        /// Check if activation token exists
        /// </summary>
        public static bool HasToken()
        {
            string token = ReadToken();
            return !string.IsNullOrEmpty(token);
        }

        /// <summary>
        /// Get device ID for activation (MAC address hash)
        /// </summary>
        public static string GetDeviceId()
        {
            try
            {
                // Get first active network adapter MAC address
                var networkInterfaces = System.Net.NetworkInformation.NetworkInterface.GetAllNetworkInterfaces();
                foreach (var adapter in networkInterfaces)
                {
                    if (adapter.OperationalStatus == System.Net.NetworkInformation.OperationalStatus.Up &&
                        adapter.NetworkInterfaceType != System.Net.NetworkInformation.NetworkInterfaceType.Loopback)
                    {
                        string macAddress = adapter.GetPhysicalAddress().ToString();
                        if (!string.IsNullOrEmpty(macAddress))
                        {
                            // Hash MAC address for privacy
                            using (var sha256 = SHA256.Create())
                            {
                                byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(macAddress));
                                return Convert.ToBase64String(hashBytes);
                            }
                        }
                    }
                }

                // Fallback: Use computer name + user name hash
                string fallback = Environment.MachineName + "_" + Environment.UserName;
                using (var sha256 = SHA256.Create())
                {
                    byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(fallback));
                    return Convert.ToBase64String(hashBytes);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting device ID: {ex.Message}");
                // Ultimate fallback
                return Convert.ToBase64String(
                    SHA256.Create().ComputeHash(
                        Encoding.UTF8.GetBytes(Environment.MachineName)
                    )
                );
            }
        }
    }
}
