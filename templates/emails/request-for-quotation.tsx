import { Heading, Text, Section, Button } from "@react-email/components";
import { Layout, InfoCard, InfoRow, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface RequestForQuotationEmailProps {
  branding: Branding;
  rfq_number: string;
  rfq_date: string;
  supplier_name?: string;
  document_link?: string;
  custom_message?: string;
}

export const RequestForQuotationEmail = ({
  branding,
  rfq_number,
  rfq_date,
  supplier_name,
  document_link,
  custom_message,
}: RequestForQuotationEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Request for Quotation
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Please review the attached request for quotation and respond with your pricing.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="RFQ No." value={rfq_number} />
        <InfoRow branding={branding} label="Date" value={rfq_date} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      {document_link && (
        <Section className="my-8">
          <Button
            className="email-button box-border w-full rounded-[4px] px-[12px] py-[12px] text-center font-medium text-[16px]"
            style={{ backgroundColor: branding.primary_color, color: branding.button_text_color || "#ffffff" }}
            href={document_link}
          >
            View Request for Quotation
          </Button>
        </Section>
      )}
    </Layout>
  );
};

// Preview with sample data
export default function RequestForQuotationEmailPreview() {
  return (
    <RequestForQuotationEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#006CFF",
        tertiary_color: "#9A9A9A",
        text_color: "#0f0f0f",
        background_color: "#f5f5f5",
        card_color: "#ffffff",
        border_color: "#e5e7eb",
        highlight_color: "#e5e7eb",
        primary_color_dark: "#4D8DFF",
        tertiary_color_dark: "#6B7280",
        text_color_dark: "#E5E7EB",
        background_color_dark: "#E5E7EB",
        card_color_dark: "#000000",
        border_color_dark: "#4b5563",
        highlight_color_dark: "#374151",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      rfq_number="RFQ-2025-001"
      rfq_date="February 12, 2025"
      supplier_name="Acme Supplies"
      document_link="https://example.com/rfq/123"
    />
  );
}
