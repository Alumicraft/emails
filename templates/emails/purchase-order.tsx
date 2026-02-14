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
        className="text-[24px] font-medium"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        New Purchase Order
      </Heading>

      <Text
        className="text-base leading-7"
        style={{ color: branding.text_color }}
      >
        Please review the attached purchase order.
      </Text>

      <InfoCard>
        <InfoRow label="PO No." value={po_number} />
        <InfoRow label="Date" value={po_date} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        className="text-base leading-7"
        style={{ color: branding.text_color }}
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
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      po_number="PO-2025-001"
      po_date="February 12, 2025"
      supplier_name="Acme Supplies"
    />
  );
}
