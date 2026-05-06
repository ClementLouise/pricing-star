/** Static list of IRP reference countries — matches backend country_reference table. */

export interface CountryRef {
  code: string;
  name: string;
  region: string;
  is_oecd19: boolean;
  is_mfn8: boolean;
  is_eu5: boolean;
}

export const COUNTRIES: CountryRef[] = [
  // Europe — EU-5
  { code: "DE", name: "Germany", region: "Europe", is_oecd19: true, is_mfn8: true, is_eu5: true },
  { code: "FR", name: "France", region: "Europe", is_oecd19: true, is_mfn8: true, is_eu5: true },
  { code: "GB", name: "United Kingdom", region: "Europe", is_oecd19: true, is_mfn8: true, is_eu5: false },
  { code: "IT", name: "Italy", region: "Europe", is_oecd19: true, is_mfn8: false, is_eu5: true },
  { code: "ES", name: "Spain", region: "Europe", is_oecd19: true, is_mfn8: false, is_eu5: true },
  // Europe — other OECD
  { code: "CH", name: "Switzerland", region: "Europe", is_oecd19: true, is_mfn8: true, is_eu5: false },
  { code: "NO", name: "Norway", region: "Europe", is_oecd19: true, is_mfn8: true, is_eu5: false },
  { code: "SE", name: "Sweden", region: "Europe", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "NL", name: "Netherlands", region: "Europe", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "BE", name: "Belgium", region: "Europe", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "AT", name: "Austria", region: "Europe", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "DK", name: "Denmark", region: "Europe", is_oecd19: true, is_mfn8: true, is_eu5: false },
  { code: "FI", name: "Finland", region: "Europe", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "PT", name: "Portugal", region: "Europe", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "IE", name: "Ireland", region: "Europe", is_oecd19: true, is_mfn8: true, is_eu5: false },
  { code: "PL", name: "Poland", region: "Europe", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "CZ", name: "Czech Republic", region: "Europe", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "HU", name: "Hungary", region: "Europe", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "SK", name: "Slovakia", region: "Europe", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "RO", name: "Romania", region: "Europe", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "GR", name: "Greece", region: "Europe", is_oecd19: false, is_mfn8: false, is_eu5: false },
  // Asia-Pacific
  { code: "JP", name: "Japan", region: "Asia-Pacific", is_oecd19: true, is_mfn8: true, is_eu5: false },
  { code: "AU", name: "Australia", region: "Asia-Pacific", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "KR", name: "South Korea", region: "Asia-Pacific", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "TW", name: "Taiwan", region: "Asia-Pacific", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "SG", name: "Singapore", region: "Asia-Pacific", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "NZ", name: "New Zealand", region: "Asia-Pacific", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "CN", name: "China", region: "Asia-Pacific", is_oecd19: false, is_mfn8: false, is_eu5: false },
  // Americas
  { code: "CA", name: "Canada", region: "Americas", is_oecd19: true, is_mfn8: true, is_eu5: false },
  { code: "BR", name: "Brazil", region: "Americas", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "MX", name: "Mexico", region: "Americas", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "AR", name: "Argentina", region: "Americas", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "CL", name: "Chile", region: "Americas", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "CO", name: "Colombia", region: "Americas", is_oecd19: false, is_mfn8: false, is_eu5: false },
  // Middle East & Africa
  { code: "SA", name: "Saudi Arabia", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "AE", name: "UAE", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "IL", name: "Israel", region: "Middle East & Africa", is_oecd19: true, is_mfn8: false, is_eu5: false },
  { code: "ZA", name: "South Africa", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "TR", name: "Turkey", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "EG", name: "Egypt", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "MA", name: "Morocco", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "NG", name: "Nigeria", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
  { code: "KE", name: "Kenya", region: "Middle East & Africa", is_oecd19: false, is_mfn8: false, is_eu5: false },
];

export const COUNTRY_MAP = Object.fromEntries(COUNTRIES.map((c) => [c.code, c]));

export const REGIONS = [...new Set(COUNTRIES.map((c) => c.region))];

export function countryFlag(code: string): string {
  return code
    .toUpperCase()
    .split("")
    .map((c) => String.fromCodePoint(0x1f1e6 - 65 + c.charCodeAt(0)))
    .join("");
}
