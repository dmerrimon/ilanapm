using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Regulatory authority information for each country
    /// </summary>
    public class CountryRegulatoryInfo
    {
        public string country_code { get; set; }
        public string country_name { get; set; }
        public string regulatory_authority { get; set; }
        public string ethics_committee_name { get; set; }
        public string approval_form_name { get; set; }

        /// <summary>
        /// Get regulatory info for a specific country
        /// </summary>
        public static CountryRegulatoryInfo GetCountryInfo(string countryCode)
        {
            var mapping = GetAllCountries();
            string code = countryCode.ToUpper();

            if (mapping.ContainsKey(code))
            {
                return mapping[code];
            }

            // Default to USA if country not found
            return mapping["USA"];
        }

        /// <summary>
        /// Get all country regulatory information
        /// </summary>
        public static Dictionary<string, CountryRegulatoryInfo> GetAllCountries()
        {
            return new Dictionary<string, CountryRegulatoryInfo>
            {
                {
                    "USA", new CountryRegulatoryInfo
                    {
                        country_code = "USA",
                        country_name = "United States",
                        regulatory_authority = "FDA",
                        ethics_committee_name = "IRB",
                        approval_form_name = "FDA Form 1572"
                    }
                },
                {
                    "GBR", new CountryRegulatoryInfo
                    {
                        country_code = "GBR",
                        country_name = "United Kingdom",
                        regulatory_authority = "MHRA",
                        ethics_committee_name = "REC",
                        approval_form_name = "EudraCT Application"
                    }
                },
                {
                    "UK", new CountryRegulatoryInfo
                    {
                        country_code = "UK",
                        country_name = "United Kingdom",
                        regulatory_authority = "MHRA",
                        ethics_committee_name = "REC",
                        approval_form_name = "EudraCT Application"
                    }
                },
                {
                    "CAN", new CountryRegulatoryInfo
                    {
                        country_code = "CAN",
                        country_name = "Canada",
                        regulatory_authority = "Health Canada",
                        ethics_committee_name = "REB",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "CANADA", new CountryRegulatoryInfo
                    {
                        country_code = "CAN",
                        country_name = "Canada",
                        regulatory_authority = "Health Canada",
                        ethics_committee_name = "REB",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "AUS", new CountryRegulatoryInfo
                    {
                        country_code = "AUS",
                        country_name = "Australia",
                        regulatory_authority = "TGA",
                        ethics_committee_name = "HREC",
                        approval_form_name = "CTN/CTA Application"
                    }
                },
                {
                    "AUSTRALIA", new CountryRegulatoryInfo
                    {
                        country_code = "AUS",
                        country_name = "Australia",
                        regulatory_authority = "TGA",
                        ethics_committee_name = "HREC",
                        approval_form_name = "CTN/CTA Application"
                    }
                },
                {
                    "BRA", new CountryRegulatoryInfo
                    {
                        country_code = "BRA",
                        country_name = "Brazil",
                        regulatory_authority = "ANVISA",
                        ethics_committee_name = "CEP",
                        approval_form_name = "Plataforma Brasil Application"
                    }
                },
                {
                    "BRAZIL", new CountryRegulatoryInfo
                    {
                        country_code = "BRA",
                        country_name = "Brazil",
                        regulatory_authority = "ANVISA",
                        ethics_committee_name = "CEP",
                        approval_form_name = "Plataforma Brasil Application"
                    }
                },
                {
                    "CHN", new CountryRegulatoryInfo
                    {
                        country_code = "CHN",
                        country_name = "China",
                        regulatory_authority = "NMPA",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "IND Application"
                    }
                },
                {
                    "CHINA", new CountryRegulatoryInfo
                    {
                        country_code = "CHN",
                        country_name = "China",
                        regulatory_authority = "NMPA",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "IND Application"
                    }
                },
                {
                    "IND", new CountryRegulatoryInfo
                    {
                        country_code = "IND",
                        country_name = "India",
                        regulatory_authority = "CDSCO",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "CT-01 Form"
                    }
                },
                {
                    "INDIA", new CountryRegulatoryInfo
                    {
                        country_code = "IND",
                        country_name = "India",
                        regulatory_authority = "CDSCO",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "CT-01 Form"
                    }
                },
                {
                    "MEX", new CountryRegulatoryInfo
                    {
                        country_code = "MEX",
                        country_name = "Mexico",
                        regulatory_authority = "COFEPRIS",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "MEXICO", new CountryRegulatoryInfo
                    {
                        country_code = "MEX",
                        country_name = "Mexico",
                        regulatory_authority = "COFEPRIS",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "ZAF", new CountryRegulatoryInfo
                    {
                        country_code = "ZAF",
                        country_name = "South Africa",
                        regulatory_authority = "SAHPRA",
                        ethics_committee_name = "HREC",
                        approval_form_name = "CTA Application"
                    }
                },
                {
                    "SOUTH AFRICA", new CountryRegulatoryInfo
                    {
                        country_code = "ZAF",
                        country_name = "South Africa",
                        regulatory_authority = "SAHPRA",
                        ethics_committee_name = "HREC",
                        approval_form_name = "CTA Application"
                    }
                },
                {
                    "THA", new CountryRegulatoryInfo
                    {
                        country_code = "THA",
                        country_name = "Thailand",
                        regulatory_authority = "Thai FDA",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "THAILAND", new CountryRegulatoryInfo
                    {
                        country_code = "THA",
                        country_name = "Thailand",
                        regulatory_authority = "Thai FDA",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "VNM", new CountryRegulatoryInfo
                    {
                        country_code = "VNM",
                        country_name = "Vietnam",
                        regulatory_authority = "DAV",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Registration"
                    }
                },
                {
                    "VIETNAM", new CountryRegulatoryInfo
                    {
                        country_code = "VNM",
                        country_name = "Vietnam",
                        regulatory_authority = "DAV",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Registration"
                    }
                },
                {
                    "BGD", new CountryRegulatoryInfo
                    {
                        country_code = "BGD",
                        country_name = "Bangladesh",
                        regulatory_authority = "DGDA",
                        ethics_committee_name = "National Research Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "BANGLADESH", new CountryRegulatoryInfo
                    {
                        country_code = "BGD",
                        country_name = "Bangladesh",
                        regulatory_authority = "DGDA",
                        ethics_committee_name = "National Research Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "COD", new CountryRegulatoryInfo
                    {
                        country_code = "COD",
                        country_name = "DRC",
                        regulatory_authority = "DMP",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "DRC", new CountryRegulatoryInfo
                    {
                        country_code = "COD",
                        country_name = "DRC",
                        regulatory_authority = "DMP",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "GIN", new CountryRegulatoryInfo
                    {
                        country_code = "GIN",
                        country_name = "Guinea",
                        regulatory_authority = "DNP",
                        ethics_committee_name = "National Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "GUINEA", new CountryRegulatoryInfo
                    {
                        country_code = "GIN",
                        country_name = "Guinea",
                        regulatory_authority = "DNP",
                        ethics_committee_name = "National Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "KEN", new CountryRegulatoryInfo
                    {
                        country_code = "KEN",
                        country_name = "Kenya",
                        regulatory_authority = "PPB",
                        ethics_committee_name = "ERC",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "KENYA", new CountryRegulatoryInfo
                    {
                        country_code = "KEN",
                        country_name = "Kenya",
                        regulatory_authority = "PPB",
                        ethics_committee_name = "ERC",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "LBR", new CountryRegulatoryInfo
                    {
                        country_code = "LBR",
                        country_name = "Liberia",
                        regulatory_authority = "LMHRA",
                        ethics_committee_name = "National Research Ethics Board",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "LIBERIA", new CountryRegulatoryInfo
                    {
                        country_code = "LBR",
                        country_name = "Liberia",
                        regulatory_authority = "LMHRA",
                        ethics_committee_name = "National Research Ethics Board",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "MWI", new CountryRegulatoryInfo
                    {
                        country_code = "MWI",
                        country_name = "Malawi",
                        regulatory_authority = "PMRA",
                        ethics_committee_name = "NHSRC",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "MALAWI", new CountryRegulatoryInfo
                    {
                        country_code = "MWI",
                        country_name = "Malawi",
                        regulatory_authority = "PMRA",
                        ethics_committee_name = "NHSRC",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "MLI", new CountryRegulatoryInfo
                    {
                        country_code = "MLI",
                        country_name = "Mali",
                        regulatory_authority = "DPM",
                        ethics_committee_name = "CNESS",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "MALI", new CountryRegulatoryInfo
                    {
                        country_code = "MLI",
                        country_name = "Mali",
                        regulatory_authority = "DPM",
                        ethics_committee_name = "CNESS",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "PER", new CountryRegulatoryInfo
                    {
                        country_code = "PER",
                        country_name = "Peru",
                        regulatory_authority = "DIGEMID",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "PERU", new CountryRegulatoryInfo
                    {
                        country_code = "PER",
                        country_name = "Peru",
                        regulatory_authority = "DIGEMID",
                        ethics_committee_name = "Ethics Committee",
                        approval_form_name = "Clinical Trial Authorization"
                    }
                },
                {
                    "SLE", new CountryRegulatoryInfo
                    {
                        country_code = "SLE",
                        country_name = "Sierra Leone",
                        regulatory_authority = "PMRA",
                        ethics_committee_name = "National Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "SIERRA LEONE", new CountryRegulatoryInfo
                    {
                        country_code = "SLE",
                        country_name = "Sierra Leone",
                        regulatory_authority = "PMRA",
                        ethics_committee_name = "National Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "TZA", new CountryRegulatoryInfo
                    {
                        country_code = "TZA",
                        country_name = "Tanzania",
                        regulatory_authority = "TFDA",
                        ethics_committee_name = "NIMR Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "TANZANIA", new CountryRegulatoryInfo
                    {
                        country_code = "TZA",
                        country_name = "Tanzania",
                        regulatory_authority = "TFDA",
                        ethics_committee_name = "NIMR Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "UGA", new CountryRegulatoryInfo
                    {
                        country_code = "UGA",
                        country_name = "Uganda",
                        regulatory_authority = "NDA",
                        ethics_committee_name = "Research Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "UGANDA", new CountryRegulatoryInfo
                    {
                        country_code = "UGA",
                        country_name = "Uganda",
                        regulatory_authority = "NDA",
                        ethics_committee_name = "Research Ethics Committee",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "ZWE", new CountryRegulatoryInfo
                    {
                        country_code = "ZWE",
                        country_name = "Zimbabwe",
                        regulatory_authority = "MCAZ",
                        ethics_committee_name = "Research Council of Zimbabwe",
                        approval_form_name = "Clinical Trial Application"
                    }
                },
                {
                    "ZIMBABWE", new CountryRegulatoryInfo
                    {
                        country_code = "ZWE",
                        country_name = "Zimbabwe",
                        regulatory_authority = "MCAZ",
                        ethics_committee_name = "Research Council of Zimbabwe",
                        approval_form_name = "Clinical Trial Application"
                    }
                }
            };
        }
    }
}
