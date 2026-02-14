import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface SalesOrderEmailProps {
  branding: Branding;
  order_number: string;
  order_date: string;
  project_name?: string;
  customer_name?: string;
  order_total: string;
  custom_message?: string;
}

export const SalesOrderEmail = ({
  branding,
  order_number,
  order_date,
  project_name,
  customer_name,
  order_total,
  custom_message,
}: SalesOrderEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Order Confirmation
      </Heading>

      <Text
        className="text-sm leading-6"
        style={{ color: branding.text_color }}
      >
        Your order has been confirmed. Please review the attached PDF.
      </Text>

      <InfoCard>
        <InfoRow label="Order No." value={order_number} />
        {project_name && <InfoRow label="Project" value={project_name} />}
        <InfoAmount label="Order Total" value={order_total} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        className="text-sm leading-6"
        style={{ color: branding.tertiary_color }}
      >
        <em>Thank you for your business!</em>
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function SalesOrderEmailPreview() {
  return (
    <SalesOrderEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      order_number="SO-2025-001"
      order_date="February 12, 2025"
      project_name="Website Redesign"
      customer_name="John"
      order_total="$1,250.00"
    />
  );
}
