import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface DocumentEmailProps {
  branding: Branding;
  document_type: string;
  document_number: string;
  document_date?: string;
  total_amount?: string;
  customer_name?: string;
  party_name?: string;
  custom_message?: string;
}

export const DocumentEmail = ({
  branding,
  document_type,
  document_number,
  document_date,
  total_amount,
  customer_name,
  party_name,
  custom_message,
}: DocumentEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        New {document_type || "Document"}
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Please find the attached {document_type?.toLowerCase() || "document"} for your reference.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label={document_type || "Document"} value={document_number} />
        {document_date && <InfoRow branding={branding} label="Date" value={document_date} />}
        {total_amount && <InfoAmount branding={branding} label="Total" value={total_amount} />}
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
export default function DocumentEmailPreview() {
  return (
    <DocumentEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      document_type="Delivery Note"
      document_number="DN-2025-001"
      document_date="February 12, 2025"
      total_amount="$1,250.00"
      customer_name="John"
    />
  );
}
