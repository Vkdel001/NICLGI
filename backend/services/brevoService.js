import SibApiV3Sdk from '@getbrevo/brevo';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Function to format currency amounts
const formatCurrency = (amount) => {
  try {
    console.log(`💰 Formatting currency: ${amount} (type: ${typeof amount})`);
    // Convert to number and round to nearest integer
    const numAmount = parseFloat(amount.toString().replace(/,/g, ''));
    const rounded = Math.round(numAmount);
    // Format with commas
    const formatted = rounded.toLocaleString();
    console.log(`💰 Formatted result: ${formatted}`);
    return formatted;
  } catch (error) {
    console.error(`💰 Currency formatting error:`, error);
    // Fallback: return original amount if formatting fails
    return amount;
  }
};

// Initialize Brevo API
let apiInstance;
try {
  // Check if we have the API key
  if (!process.env.BREVO_API_KEY) {
    throw new Error('BREVO_API_KEY environment variable is not set');
  }

  // Initialize API client
  const defaultClient = SibApiV3Sdk.ApiClient.instance;
  if (defaultClient && defaultClient.authentications) {
    const apiKeyAuth = defaultClient.authentications['api-key'];
    apiKeyAuth.apiKey = process.env.BREVO_API_KEY;
  }

  apiInstance = new SibApiV3Sdk.TransactionalEmailsApi();
  console.log('✅ Brevo API initialized successfully');
} catch (error) {
  console.error('❌ Brevo API initialization error:', error);
  // Create a basic instance without authentication for now
  apiInstance = new SibApiV3Sdk.TransactionalEmailsApi();
}

// Team-specific sender configurations
const SENDER_CONFIG = {
  motor: {
    name: 'NICL Motor',
    email: 'noreply@niclmauritius.site',
    replyTo: 'motor@niclmauritius.site'
  },
  health: {
    name: 'NICL Health',
    email: 'noreply@niclmauritius.site',
    replyTo: 'health@niclmauritius.site'
  }
};

/**
 * Send renewal emails with PDFs attached
 * @param {string} team - 'motor' or 'health'
 * @param {Array} recipients - Array of recipient objects with email, name, policyNo, etc.
 * @param {string} pdfDirectory - Directory containing the PDF files
 * @returns {Promise} - Results of email sending
 */
export const sendRenewalEmails = async (team, recipients, pdfDirectory) => {
  const senderConfig = SENDER_CONFIG[team];
  if (!senderConfig) {
    throw new Error(`Invalid team: ${team}`);
  }

  const results = {
    success: 0,
    failed: 0,
    errors: []
  };

  console.log(`📧 Starting ${team} email sending for ${recipients.length} recipients`);

  for (const recipient of recipients) {
    try {
      // Find the PDF file for this recipient
      const pdfPath = await findPDFForRecipient(recipient, pdfDirectory);

      if (!pdfPath) {
        results.failed++;
        results.errors.push({
          email: recipient.email,
          error: 'PDF file not found'
        });
        continue;
      }

      // Read PDF file and convert to base64
      const pdfBuffer = await fs.readFile(pdfPath);
      const pdfBase64 = pdfBuffer.toString('base64');

      // Create email content
      const emailContent = createEmailContent(team, recipient);

      // Prepare email data
      const sendSmtpEmail = new SibApiV3Sdk.SendSmtpEmail();

      sendSmtpEmail.sender = {
        name: senderConfig.name,
        email: senderConfig.email
      };

      sendSmtpEmail.to = [{
        email: recipient.email,
        name: recipient.name || recipient.email
      }];

      sendSmtpEmail.replyTo = {
        email: senderConfig.replyTo,
        name: senderConfig.name
      };

      sendSmtpEmail.subject = `${senderConfig.name} - Insurance Renewal Notice - Policy ${recipient.policyNo || 'N/A'}`;

      sendSmtpEmail.htmlContent = emailContent.html;
      sendSmtpEmail.textContent = emailContent.text;

      // Attach PDF
      sendSmtpEmail.attachment = [{
        content: pdfBase64,
        name: path.basename(pdfPath),
        type: 'application/pdf'
      }];

      // Send email with API key in headers
      const opts = {
        'headers': {
          'api-key': process.env.BREVO_API_KEY
        }
      };
      await apiInstance.sendTransacEmail(sendSmtpEmail, opts);

      results.success++;
      console.log(`✅ Email sent to ${recipient.email} (${recipient.name || 'N/A'})`);

    } catch (error) {
      results.failed++;
      results.errors.push({
        email: recipient.email,
        error: error.message
      });
      console.error(`❌ Failed to send email to ${recipient.email}:`, error.message);
    }
  }

  console.log(`📊 Email sending completed: ${results.success} success, ${results.failed} failed`);
  return results;
};

/**
 * Find PDF file for a specific recipient
 */
const findPDFForRecipient = async (recipient, pdfDirectory) => {
  try {
    const files = await fs.readdir(pdfDirectory);
    const pdfFiles = files.filter(file => file.endsWith('.pdf'));

    // First try exact filename match (if expectedFilename is provided)
    if (recipient.expectedFilename) {
      const exactMatch = pdfFiles.find(file => file === recipient.expectedFilename);
      if (exactMatch) {
        console.log(`✅ Found exact PDF match: ${exactMatch} for ${recipient.email}`);
        return path.join(pdfDirectory, exactMatch);
      } else {
        console.log(`⚠️ Expected PDF not found: ${recipient.expectedFilename} for ${recipient.email}`);
      }
    }

    // Fallback: Try to match by policy number or name
    const searchTerms = [
      recipient.policyNo,
      recipient.name,
      recipient.email.split('@')[0]
    ].filter(Boolean);

    for (const term of searchTerms) {
      const matchingFile = pdfFiles.find(file =>
        file.toLowerCase().includes(term.toLowerCase().replace(/[^a-z0-9]/gi, '_'))
      );

      if (matchingFile) {
        console.log(`📎 Found fallback PDF match: ${matchingFile} for ${recipient.email}`);
        return path.join(pdfDirectory, matchingFile);
      }
    }

    console.log(`❌ No PDF found for ${recipient.email} (${recipient.name})`);
    return null;

  } catch (error) {
    console.error('Error finding PDF file:', error);
    return null;
  }
};

/**
 * Create email content based on team and recipient
 */
const createEmailContent = (team, recipient) => {
  const isMotor = team === 'motor';
  const teamName = isMotor ? 'Motor Insurance' : 'Healthcare Insurance';
  const primaryColor = isMotor ? '#1e40af' : '#059669';

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${teamName} Renewal Notice</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: ${primaryColor}; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">NICL ${isMotor ? 'Motor' : 'Health'}</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">National Insurance Company Limited</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2 style="color: ${primaryColor}; margin-top: 0;">${teamName} Renewal Notice</h2>
            
            <p>Dear ${recipient.name || 'Valued Customer'},</p>
            
            ${isMotor ? `
            <p>This is a reminder that your NIC Motor Insurance Policy No. <strong>${recipient.policyNo}</strong> is due to expire on <strong>${recipient.expiryDate}</strong>. To ensure your continued coverage and peace of mind, you are invited to renew your policy before the expiry date.</p>
            
            <h3 style="color: ${primaryColor}; margin: 30px 0 15px 0;">Your Renewal Details</h3>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #f8f9fa;">
                    <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 40%;">Item</td>
                    <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">Details</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">Policy Number</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">${recipient.policyNo}</td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 12px; border: 1px solid #ddd;">Current Expiry Date</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">${recipient.expiryDate}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd;">Proposed Renewal Period</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">${recipient.renewalStart} to ${recipient.renewalEnd}</td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 12px; border: 1px solid #ddd;">Renewal Premium</td>
                    <td style="padding: 12px; border: 1px solid #ddd;"><strong>MUR ${formatCurrency(recipient.premium)}</strong></td>
                </tr>
            </table>
            ` : `
            <p>We hope this email finds you well.</p>
            
            <p>Please find attached your <strong>${teamName} Renewal Notice</strong> ${recipient.policyNo ? `for Policy No. <strong>${recipient.policyNo}</strong>` : ''}.</p>
            
            <div style="background: white; padding: 20px; border-radius: 6px; border-left: 4px solid ${primaryColor}; margin: 20px 0;">
                <h3 style="margin-top: 0; color: ${primaryColor};">Important Information:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Please review the renewal terms and conditions carefully</li>
                    <li>Complete and return the renewal acceptance form if you wish to renew</li>
                    <li>Contact us if you have any questions or need assistance</li>
                    <li>Update your medical information if there have been any changes</li>
                </ul>
            </div>
            `}
            
            <p>For your convenience, you may also settle payments instantly via the QR Code included in your renewal notice using mobile banking apps such as Juice, MauBank WithMe, Blink, MyT Money, or other supported applications.</p>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Need Help?</strong></p>
                <p style="margin: 5px 0 0 0;">Contact our Customer Service team at <strong>602 3000</strong> or email us at <a href="mailto:customerservice@nicl.mu" style="color: ${primaryColor};">customerservice@nicl.mu</a></p>
            </div>
            
            <p>Thank you for choosing NICL for your insurance needs.</p>
            
            <p style="margin-bottom: 0;">Best regards,<br>
            <strong>NICL ${isMotor ? 'Motor' : 'Health'} Team</strong><br>
            National Insurance Company Limited</p>
        </div>
        

    </body>
    </html>
  `;

  const text = `
NICL ${isMotor ? 'Motor' : 'Health'} - ${teamName} Renewal Notice

Dear ${recipient.name || 'Valued Customer'},

${isMotor ? `
This is a reminder that your NIC Motor Insurance Policy No. ${recipient.policyNo} is due to expire on ${recipient.expiryDate}. To ensure your continued coverage and peace of mind, you are invited to renew your policy before the expiry date.

Your Renewal Details:
- Policy Number: ${recipient.policyNo}
- Current Expiry Date: ${recipient.expiryDate}
- Proposed Renewal Period: ${recipient.renewalStart} to ${recipient.renewalEnd}
- Renewal Premium: MUR ${formatCurrency(recipient.premium)}
` : `
Please find attached your ${teamName} Renewal Notice for Policy No. ${recipient.policyNo}.

Important Information:
- Please review the renewal terms and conditions carefully
- Complete and return the renewal acceptance form if you wish to renew
- Contact us if you have any questions or need assistance
- Update your medical information if there have been any changes
`}

For your convenience, you may also settle payments instantly via the QR Code included in your renewal notice using mobile banking apps.

Need Help?
Contact our Customer Service team at 602 3000 or email customerservice@nicl.mu

Thank you for choosing NICL for your insurance needs.

Best regards,
NICL ${isMotor ? 'Motor' : 'Health'} Team
National Insurance Company Limited

`.trim();

  return { html, text };
};

export default { sendRenewalEmails };