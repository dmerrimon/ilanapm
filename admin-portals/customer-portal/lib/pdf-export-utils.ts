/**
 * Utility functions for exporting data to PDF format with charts and tables
 */

import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import html2canvas from 'html2canvas';

/**
 * Generate filename with timestamp
 */
export function generatePDFFilename(prefix: string): string {
  const now = new Date();
  const timestamp = now.toISOString().split('T')[0]; // YYYY-MM-DD
  return `${prefix}-${timestamp}.pdf`;
}

/**
 * Capture an HTML element as an image
 */
export async function captureElementAsImage(element: HTMLElement): Promise<string> {
  const canvas = await html2canvas(element, {
    backgroundColor: '#ffffff',
    logging: false
  } as any); // Type assertion for compatibility
  return canvas.toDataURL('image/png');
}

/**
 * Add a section header to the PDF
 */
function addSectionHeader(doc: jsPDF, title: string, yPosition: number): number {
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.text(title, 14, yPosition);
  return yPosition + 8; // Return new Y position
}

/**
 * Export usage analytics to PDF with charts
 */
export async function exportUsageAnalyticsPDF(data: {
  timeRange: string;
  stats: {
    templates_generated: number;
    feedback_submissions: number;
    active_users: number;
    avg_response_time: number;
  };
  chartElements: {
    dailyActivity?: HTMLElement | null;
    templateUsage?: HTMLElement | null;
    userActivity?: HTMLElement | null;
    countryData?: HTMLElement | null;
  };
  tableData: {
    templateUsage: Array<{ template_name: string; count: number }>;
    userActivity: Array<{ user_name: string; templates_generated: number }>;
    countryData: Array<{ country: string; count: number }>;
    dailyActivity: Array<{ date: string; count: number }>;
  };
}) {
  const doc = new jsPDF('p', 'mm', 'a4');
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  let yPos = 20;

  // Title Page
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.text('Usage Analytics Report', pageWidth / 2, yPos, { align: 'center' });

  yPos += 10;
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.text(`Time Range: ${data.timeRange}`, pageWidth / 2, yPos, { align: 'center' });
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, pageWidth / 2, yPos + 6, { align: 'center' });

  yPos += 20;

  // Summary Statistics
  yPos = addSectionHeader(doc, 'Summary Statistics', yPos);

  autoTable(doc, {
    startY: yPos,
    head: [['Metric', 'Value']],
    body: [
      ['Templates Generated', data.stats.templates_generated.toString()],
      ['Feedback Submissions', data.stats.feedback_submissions.toString()],
      ['Active Users', data.stats.active_users.toString()],
      ['Avg Response Time', `${data.stats.avg_response_time}s`]
    ],
    theme: 'striped',
    headStyles: { fillColor: [0, 0, 0] },
  });

  yPos = (doc as any).lastAutoTable.finalY + 15;

  // Daily Activity Chart
  if (data.chartElements.dailyActivity) {
    if (yPos > pageHeight - 80) {
      doc.addPage();
      yPos = 20;
    }

    yPos = addSectionHeader(doc, 'Daily Template Generation', yPos);

    try {
      const dailyChartImage = await captureElementAsImage(data.chartElements.dailyActivity);
      const imgWidth = pageWidth - 28;
      const imgHeight = 60;
      doc.addImage(dailyChartImage, 'PNG', 14, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10;
    } catch (error) {
      console.error('Error capturing daily activity chart:', error);
    }

    // Daily Activity Table
    autoTable(doc, {
      startY: yPos,
      head: [['Date', 'Templates Generated']],
      body: data.tableData.dailyActivity.map(item => [item.date, item.count.toString()]),
      theme: 'grid',
      headStyles: { fillColor: [0, 0, 0] },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;
  }

  // Template Usage Chart
  if (data.chartElements.templateUsage) {
    if (yPos > pageHeight - 80) {
      doc.addPage();
      yPos = 20;
    }

    yPos = addSectionHeader(doc, 'Most Used Templates', yPos);

    try {
      const templateChartImage = await captureElementAsImage(data.chartElements.templateUsage);
      const imgWidth = (pageWidth - 28) / 2;
      const imgHeight = 70;
      doc.addImage(templateChartImage, 'PNG', 14, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10;
    } catch (error) {
      console.error('Error capturing template usage chart:', error);
    }

    // Template Usage Table
    autoTable(doc, {
      startY: yPos,
      head: [['Template Name', 'Count']],
      body: data.tableData.templateUsage.map(item => [item.template_name, item.count.toString()]),
      theme: 'grid',
      headStyles: { fillColor: [0, 0, 0] },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;
  }

  // User Activity Chart
  if (data.chartElements.userActivity) {
    if (yPos > pageHeight - 80) {
      doc.addPage();
      yPos = 20;
    }

    yPos = addSectionHeader(doc, 'Most Active Users', yPos);

    try {
      const userChartImage = await captureElementAsImage(data.chartElements.userActivity);
      const imgWidth = (pageWidth - 28) / 2;
      const imgHeight = 70;
      doc.addImage(userChartImage, 'PNG', 14, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10;
    } catch (error) {
      console.error('Error capturing user activity chart:', error);
    }

    // User Activity Table
    autoTable(doc, {
      startY: yPos,
      head: [['User Name', 'Templates Generated']],
      body: data.tableData.userActivity.map(item => [item.user_name, item.templates_generated.toString()]),
      theme: 'grid',
      headStyles: { fillColor: [0, 0, 0] },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;
  }

  // Country Data Chart
  if (data.chartElements.countryData) {
    if (yPos > pageHeight - 80) {
      doc.addPage();
      yPos = 20;
    }

    yPos = addSectionHeader(doc, 'Templates by Regulatory Authority', yPos);

    try {
      const countryChartImage = await captureElementAsImage(data.chartElements.countryData);
      const imgWidth = pageWidth - 28;
      const imgHeight = 60;
      doc.addImage(countryChartImage, 'PNG', 14, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10;
    } catch (error) {
      console.error('Error capturing country data chart:', error);
    }

    // Country Data Table
    autoTable(doc, {
      startY: yPos,
      head: [['Regulatory Authority', 'Template Count']],
      body: data.tableData.countryData.map(item => [item.country, item.count.toString()]),
      theme: 'grid',
      headStyles: { fillColor: [0, 0, 0] },
    });
  }

  // Add page numbers
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(10);
    doc.text(
      `Page ${i} of ${pageCount}`,
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    );
  }

  // Save the PDF
  const filename = generatePDFFilename(`usage-analytics-${data.timeRange}`);
  doc.save(filename);
}
