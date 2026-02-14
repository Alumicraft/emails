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

      <InfoCard>
        <InfoRow label="RFQ No." value={rfq_number} />
        <InfoRow label="Date" value={rfq_date} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      {document_link && (
        <Section className="my-8">
          <Button
            className="box-border w-full rounded-[6px] px-[12px] py-[12px] text-center font-medium text-white text-[16px]"
            style={{ backgroundColor: branding.primary_color }}
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
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      rfq_number="RFQ-2025-001"
      rfq_date="February 12, 2025"
      supplier_name="Acme Supplies"
      document_link="https://example.com/rfq/123"
    />
  );
}
