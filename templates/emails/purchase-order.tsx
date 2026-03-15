import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface PurchaseOrderEmailProps {
  branding: Branding;
  po_number: string;
  po_date: string;
  supplier_name?: string;
  custom_message?: string;
}

export const PurchaseOrderEmail = ({
  branding,
  po_number,
  po_date,
  supplier_name,
  custom_message,
}: PurchaseOrderEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="email-heading"
        style={{ color: branding.text_color, marginTop: 0, fontSize: "24px", fontWeight: 500, lineHeight: "32px" }}
      >
        New Purchase Order
      </Heading>

      <Text
        className="email-text"
        style={{ color: branding.text_color, fontSize: "15px", lineHeight: "24px" }}
      >
        Please review the attached purchase order.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="PO No." value={po_number} />
        <InfoRow branding={branding} label="Date" value={po_date} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        style={{ color: branding.text_color, fontSize: "15px", lineHeight: "24px" }}
      >
        The PDF is attached for your review. Please reach out if you have any questions or concerns.
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function PurchaseOrderEmailPreview() {
  return (
    <PurchaseOrderEmail
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
      po_number="PO-2025-001"
      po_date="February 12, 2025"
      supplier_name="Acme Supplies"
    />
  );
}
