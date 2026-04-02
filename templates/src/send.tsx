import type { VercelRequest, VercelResponse } from "@vercel/node";
import { Resend } from "resend";
import { render } from "@react-email/render";
import * as React from "react";

import { MagicLinkEmail } from "../emails/magic-link";
import { SalesInvoiceEmail } from "../emails/sales-invoice";
import { QuotationEmail } from "../emails/quotation";
import { SalesOrderEmail } from "../emails/sales-order";
import { PurchaseOrderEmail } from "../emails/purchase-order";
import { RequestForQuotationEmail } from "../emails/request-for-quotation";
import { PasswordResetEmail } from "../emails/password-reset";
import { EmailVerificationEmail } from "../emails/email-verification";
import { WelcomeEmail } from "../emails/welcome";
import { PaymentRequestEmail } from "../emails/payment-request";
import { PaymentEntryEmail } from "../emails/payment-entry";
import { DocumentEmail } from "../emails/document";
import { AchPaymentUpcoming } from "../emails/ach-payment-upcoming";
import { AchPaymentSuccess } from "../emails/ach-payment-success";
import { AchPaymentFailure } from "../emails/ach-payment-failure";
import { RetailerApplication } from "../emails/retailer-application";
import { DealerWelcome } from "../emails/dealer-welcome";
import { DealerAgreementSent } from "../emails/dealer-agreement-sent";
import { DealerAgreementSigned } from "../emails/dealer-agreement-signed";
import { FlooringPacketSent } from "../emails/flooring-packet-sent";
import { FlooringPacketSigned } from "../emails/flooring-packet-signed";
import { LoanDisbursed } from "../emails/loan-disbursed";
import { FactoryLoaReceived } from "../emails/factory-loa-received";
import { PreApproval } from "../emails/pre-approval";
import { AutopaySetup } from "../emails/autopay-setup";
import { AutopayUpdate } from "../emails/autopay-update";
import { AutopayConnected } from "../emails/autopay-connected";
import { Branding } from "../emails/shared";

const resend = new Resend(process.env.RESEND_API_KEY);

// ============================================================================
// HELPERS
// ============================================================================

function cleanEmailList(input: string | string[] | undefined): string[] {
  if (!input) return [];
  const raw = Array.isArray(input) ? input : [input];
  return raw
    .flatMap((e) => e.split(","))
    .map((e) => e.trim())
    .filter((e) => e.length > 0 && e.includes("@"));
}

// ============================================================================
// INTERFACES
// ============================================================================

interface EmailRequest {
  template: string;
  to: string | string[];
  cc?: string | string[];
  bcc?: string | string[];
  subject: string;
  data: Record<string, any>;
  branding: Branding;
  attachments?: Array<{ filename: string; content: string }>;
  from_email: string;
  from_name: string;
  reply_to?: string;
  tags?: Array<{ name: string; value: string }>;
}

// ============================================================================
// TEMPLATE REGISTRY
// ============================================================================

const templates: Record<string, React.FC<any>> = {
  "magic-link": MagicLinkEmail,
  "sales-invoice": SalesInvoiceEmail,
  "quotation": QuotationEmail,
  "sales-order": SalesOrderEmail,
  "purchase-order": PurchaseOrderEmail,
  "request-for-quotation": RequestForQuotationEmail,
  "password-reset": PasswordResetEmail,
  "email-verification": EmailVerificationEmail,
  "welcome": WelcomeEmail,
  "payment-request": PaymentRequestEmail,
  "payment-entry": PaymentEntryEmail,
  "document": DocumentEmail,
  "ach-payment-upcoming": AchPaymentUpcoming,
  "ach-payment-success": AchPaymentSuccess,
  "ach-payment-failure": AchPaymentFailure,
  "retailer-application": RetailerApplication,
  "dealer-welcome": DealerWelcome,
  "dealer-agreement-sent": DealerAgreementSent,
  "dealer-agreement-signed": DealerAgreementSigned,
  "flooring-packet-sent": FlooringPacketSent,
  "flooring-packet-signed": FlooringPacketSigned,
  "loan-disbursed": LoanDisbursed,
  "factory-loa-received": FactoryLoaReceived,
  "pre-approval": PreApproval,
  "autopay-setup": AutopaySetup,
  "autopay-update": AutopayUpdate,
  "autopay-connected": AutopayConnected,
};

// ============================================================================
// HANDLER
// ============================================================================

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method === "GET") {
    return res.status(200).json({ status: "ok", templates: Object.keys(templates) });
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const authHeader = req.headers.authorization;
  if (authHeader !== "Bearer " + process.env.SERVICE_API_KEY) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  try {
    const body: EmailRequest = req.body;

    const Template = templates[body.template];
    if (!Template) {
      return res.status(400).json({
        error: "Template '" + body.template + "' not found. Available: " + Object.keys(templates).join(", "),
      });
    }

    const attachments: Array<{ filename: string; content: string; content_type?: string }> = [];

    if (body.attachments) {
      for (const att of body.attachments) {
        attachments.push({ filename: att.filename, content: att.content });
      }
    }

    // For logos, use a publicly accessible URL instead of CID embedding
    // CID embedding has poor support across email clients
    let logoUrl = body.branding.logo_url || "";

    const html = await render(
      React.createElement(Template, {
        ...body.data,
        branding: { ...body.branding, logo_url: logoUrl },
      })
    );

    const to = cleanEmailList(body.to);
    if (to.length === 0) {
      return res.status(400).json({ error: "No valid recipient email addresses" });
    }
    const cc = cleanEmailList(body.cc);
    const bcc = cleanEmailList(body.bcc);

    const result = await resend.emails.send({
      from: body.from_name + " <" + body.from_email + ">",
      to,
      cc: cc.length > 0 ? cc : undefined,
      bcc: bcc.length > 0 ? bcc : undefined,
      subject: body.subject,
      html,
      attachments: attachments.length > 0 ? attachments : undefined,
      replyTo: body.reply_to,
      tags: body.tags,
    });

    if (result.error) {
      console.error("Resend error:", result.error);
      return res.status(500).json({ error: result.error.message });
    }

    return res.status(200).json({ message_id: result.data?.id, html });
  } catch (error) {
    console.error("Email send error:", error);
    return res.status(500).json({
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
}
