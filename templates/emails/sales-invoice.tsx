import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface SalesInvoiceEmailProps {
  branding: Branding;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  terms?: string;
  project_name?: string;
  customer_name?: string;
  amount_due: string;
  custom_message?: string;
}

export const SalesInvoiceEmail = ({
  branding,
  invoice_number,
  invoice_date,
  due_date,
  terms,
  project_name,
  customer_name,
  amount_due,
  custom_message,
}: SalesInvoiceEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        New Invoice
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Please review the attached invoice and submit payment at your earliest convenience.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Invoice No." value={invoice_number} />
        {project_name && <InfoRow branding={branding} label="Project" value={project_name} />}
        <InfoRow branding={branding} label="Due Date" value={due_date} valueColor="#d97706" />
        <InfoAmount branding={branding} label="Amount Due" value={amount_due} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        className="text-[15px] leading-6"
        style={{ color: branding.tertiary_color }}
      >
        <em>Thank you for your business!</em>
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function SalesInvoiceEmailPreview() {
  return (
    <SalesInvoiceEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      invoice_number="SINV-2025-001"
      invoice_date="February 12, 2025"
      due_date="February 27, 2025"
      terms="Net 15"
      project_name="Website Redesign"
      customer_name="John"
      amount_due="$1,250.00"
    />
  );
}
