import { Heading, Text, Section, Button } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface PaymentRequestEmailProps {
  branding: Branding;
  reference_number?: string;
  due_date?: string;
  project_name?: string;
  customer_name?: string;
  amount_requested: string;
  stripe_payment_url?: string;
  custom_message?: string;
}

export const PaymentRequestEmail = ({
  branding,
  reference_number,
  due_date,
  project_name,
  customer_name,
  amount_requested,
  stripe_payment_url,
  custom_message,
}: PaymentRequestEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="text-[24px] font-medium"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        New Invoice
      </Heading>

      <Text
        className="text-base leading-7"
        style={{ color: branding.text_color }}
      >
        Please review the attached PDF and submit payment at your earliest convenience.
      </Text>

      <InfoCard>
        {reference_number && <InfoRow label="Reference No." value={reference_number} />}
        {project_name && <InfoRow label="Project" value={project_name} />}
        {due_date && <InfoRow label="Due Date" value={due_date} valueColor="#dc2626" />}
        <InfoAmount label="Amount" value={amount_requested} />
      </InfoCard>

      {custom_message && (
        <Text style={{ color: branding.text_color, fontSize: "16px", lineHeight: "1.6", marginBottom: "24px" }}>
          {custom_message}
        </Text>
      )}

      <Text
        className="text-base leading-7"
        style={{ color: branding.tertiary_color }}
      >
        <em>Thank you for your business!</em>
      </Text>

      {stripe_payment_url && (
        <Section className="my-8">
          <Button
            className="box-border w-full rounded-[6px] px-[12px] py-[12px] text-center font-medium text-white text-[16px]"
            style={{ backgroundColor: branding.primary_color }}
            href={stripe_payment_url}
          >
            Pay Invoice
          </Button>
        </Section>
      )}
    </Layout>
  );
};

// Preview with sample data
export default function PaymentRequestEmailPreview() {
  return (
    <PaymentRequestEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#000000",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      reference_number="PR-2025-001"
      due_date="February 27, 2025"
      project_name="Website Redesign"
      customer_name="JOHN DOE"
      amount_requested="$500.00"
      stripe_payment_url="https://example.com/pay/123"
    />
  );
}
