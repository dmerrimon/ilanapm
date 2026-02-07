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
 * Export system analytics to PDF with charts
 */
export async function exportSystemAnalyticsPDF(data: {
  timeRange: string;
  systemMetrics: {
    total_templates: number;
    avg_response_time: number;
    api_requests: number;
    ml_accuracy: number;
    total_users: number;
    active_organizations: number;
  };
  chartElements: {
    dailyUsage?: HTMLElement | null;
    mlPerformance?: HTMLElement | null;
    apiEndpoints?: HTMLElement | null;
  };
  tableData: {
    dailyUsage: Array<{ date: string; templates: number; users: number }>;
    mlPerformance: Array<{ metric: string; value: number; trend: string }>;
    apiEndpoints: Array<{ endpoint: string; calls: number; avg_time: number; errors: number }>;
  };
}) {
  const doc = new jsPDF('p', 'mm', 'a4');
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  let yPos = 20;

  // Title Page
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.text('System Analytics Report', pageWidth / 2, yPos, { align: 'center' });

  yPos += 10;
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.text(`Time Range: ${data.timeRange}`, pageWidth / 2, yPos, { align: 'center' });
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, pageWidth / 2, yPos + 6, { align: 'center' });

  yPos += 20;

  // System Metrics Overview
  yPos = addSectionHeader(doc, 'System Metrics Overview', yPos);

  autoTable(doc, {
    startY: yPos,
    head: [['Metric', 'Value']],
    body: [
      ['Total Templates', data.systemMetrics.total_templates.toLocaleString()],
      ['Avg Response Time', `${data.systemMetrics.avg_response_time}s`],
      ['API Requests', data.systemMetrics.api_requests.toLocaleString()],
      ['ML Accuracy', `${data.systemMetrics.ml_accuracy}%`],
      ['Total Users', data.systemMetrics.total_users.toString()],
      ['Active Organizations', data.systemMetrics.active_organizations.toString()]
    ],
    theme: 'striped',
    headStyles: { fillColor: [0, 0, 0] },
  });

  yPos = (doc as any).lastAutoTable.finalY + 15;

  // Daily Usage Chart
  if (data.chartElements.dailyUsage) {
    if (yPos > pageHeight - 80) {
      doc.addPage();
      yPos = 20;
    }

    yPos = addSectionHeader(doc, 'Daily Platform Usage', yPos);

    try {
      const dailyChartImage = await captureElementAsImage(data.chartElements.dailyUsage);
      const imgWidth = pageWidth - 28;
      const imgHeight = 60;
      doc.addImage(dailyChartImage, 'PNG', 14, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10;
    } catch (error) {
      console.error('Error capturing daily usage chart:', error);
    }

    // Daily Usage Table
    autoTable(doc, {
      startY: yPos,
      head: [['Date', 'Templates', 'Users']],
      body: data.tableData.dailyUsage.map(item => [
        item.date,
        item.templates.toString(),
        item.users.toString()
      ]),
      theme: 'grid',
      headStyles: { fillColor: [0, 0, 0] },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;
  }

  // ML Performance Chart
  if (data.chartElements.mlPerformance) {
    if (yPos > pageHeight - 80) {
      doc.addPage();
      yPos = 20;
    }

    yPos = addSectionHeader(doc, 'ML Model Performance', yPos);

    try {
      const mlChartImage = await captureElementAsImage(data.chartElements.mlPerformance);
      const imgWidth = (pageWidth - 28) / 2;
      const imgHeight = 70;
      doc.addImage(mlChartImage, 'PNG', 14, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10;
    } catch (error) {
      console.error('Error capturing ML performance chart:', error);
    }

    // ML Performance Table
    autoTable(doc, {
      startY: yPos,
      head: [['Metric', 'Accuracy %', 'Trend']],
      body: data.tableData.mlPerformance.map(item => [
        item.metric,
        `${item.value}%`,
        item.trend
      ]),
      theme: 'grid',
      headStyles: { fillColor: [0, 0, 0] },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;
  }

  // API Endpoints Chart
  if (data.chartElements.apiEndpoints) {
    if (yPos > pageHeight - 80) {
      doc.addPage();
      yPos = 20;
    }

    yPos = addSectionHeader(doc, 'Top API Endpoints', yPos);

    try {
      const apiChartImage = await captureElementAsImage(data.chartElements.apiEndpoints);
      const imgWidth = (pageWidth - 28) / 2;
      const imgHeight = 70;
      doc.addImage(apiChartImage, 'PNG', 14, yPos, imgWidth, imgHeight);
      yPos += imgHeight + 10;
    } catch (error) {
      console.error('Error capturing API endpoints chart:', error);
    }

    // API Endpoints Table
    autoTable(doc, {
      startY: yPos,
      head: [['Endpoint', 'Calls', 'Avg Time (s)', 'Errors']],
      body: data.tableData.apiEndpoints.map(item => [
        item.endpoint,
        item.calls.toLocaleString(),
        item.avg_time.toString(),
        item.errors.toString()
      ]),
      theme: 'grid',
      headStyles: { fillColor: [0, 0, 0] },
      styles: { fontSize: 8 },
      columnStyles: {
        0: { cellWidth: 80 }
      }
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
  const filename = generatePDFFilename(`system-analytics-${data.timeRange}`);
  doc.save(filename);
}
