using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Result from auto-fix operation
    /// </summary>
    public class AutoFixResult
    {
        public int fixes_applied { get; set; }
        public List<string> issues_fixed { get; set; }
        public int remaining_issues { get; set; }
        public Timeline modified_timeline { get; set; }
    }
}
