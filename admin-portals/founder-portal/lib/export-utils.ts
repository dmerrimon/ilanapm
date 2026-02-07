/**
 * Utility functions for exporting data to CSV format
 */

/**
 * Convert an array of objects to CSV format
 */
export function convertToCSV(data: Record<string, any>[]): string {
  if (data.length === 0) return '';

  // Get headers from the first object
  const headers = Object.keys(data[0]);

  // Create CSV header row
  const csvHeaders = headers.join(',');

  // Create CSV data rows
  const csvRows = data.map(row => {
    return headers.map(header => {
      const value = row[header];
      // Handle values that might contain commas or quotes
      if (value === null || value === undefined) return '';
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return stringValue;
    }).join(',');
  });

  return [csvHeaders, ...csvRows].join('\n');
}

/**
 * Download data as CSV file
 */
export function downloadCSV(csvContent: string, filename: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');

  if (link.download !== undefined) {
    // Create a link to the file
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

/**
 * Generate filename with timestamp
 */
export function generateFilename(prefix: string, extension: string = 'csv'): string {
  const now = new Date();
  const timestamp = now.toISOString().split('T')[0]; // YYYY-MM-DD
  return `${prefix}-${timestamp}.${extension}`;
}

/**
 * Export multiple datasets as a single CSV with section headers
 */
export function exportMultipleSectionsToCSV(
  sections: Array<{ title: string; data: Record<string, any>[] }>,
  filename: string
): void {
  const csvParts: string[] = [];

  sections.forEach((section, index) => {
    if (index > 0) {
      // Add empty lines between sections
      csvParts.push('\n');
    }

    // Add section title
    csvParts.push(`# ${section.title}`);

    // Add section data
    const sectionCSV = convertToCSV(section.data);
    csvParts.push(sectionCSV);
  });

  const fullCSV = csvParts.join('\n');
  downloadCSV(fullCSV, filename);
}
