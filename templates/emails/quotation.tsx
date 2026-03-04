import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface QuotationEmailProps {
  branding: Branding;
  quotation_number: string;
  quotation_date: string;
  valid_until: string;
  customer_name?: string;
  total_amount: string;
  custom_message?: string;
}

export const QuotationEmail = ({
  branding,
  quotation_number,
  quotation_date,
  valid_until,
  customer_name,
  total_amount,
  custom_message,
}: QuotationEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        New Quotation
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Please review the attached quotation at your earliest convenience.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Quotation No." value={quotation_number} />
        <InfoRow branding={branding} label="Valid Until" value={valid_until} />
        <InfoAmount branding={branding} label="Estimated Total" value={total_amount} />
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
        <em>We look forward to working with you!</em>
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function QuotationEmailPreview() {
  return (
    <QuotationEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#006CFF",
        tertiary_color: "#9A9A9A",
        text_color: "#0f0f0f",
        background_color: "#f5f5f5",
        card_color: "#ffffff",
        border_color: "#e5e7eb",
        amount_bg_color: "#e5e7eb",
        primary_color_dark: "#4D8DFF",
        tertiary_color_dark: "#6B7280",
        text_color_dark: "#E5E7EB",
        background_color_dark: "#E5E7EB",
        card_color_dark: "#000000",
        border_color_dark: "#4b5563",
        amount_bg_color_dark: "#374151",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      quotation_number="QTN-2025-001"
      quotation_date="February 12, 2025"
      valid_until="February 27, 2025"
      customer_name="John"
      total_amount="$1,250.00"
    />
  );
}
