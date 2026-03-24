import { Heading, Text, Section } from "@react-email/components";
import { Layout, Button, InfoCard, InfoRow, Branding } from "./shared";

export { Branding } from "./shared";

export interface AutopayUpdateProps {
  branding: Branding;
  customer_name: string;
  setup_url: string;
}

export const AutopayUpdate = ({
  branding,
  customer_name,
  setup_url,
}: AutopayUpdateProps) => {
  return (
    <Layout branding={branding} preview="Update your Auto-Pay bank account">
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Update Bank Account
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Use the link below to connect a new business bank account for Auto-Pay.
        The new account will replace your current account on file and be used
        for all active and future loans.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
      </InfoCard>

      <Section style={{ textAlign: "center" as const, marginTop: "24px", marginBottom: "24px" }}>
        <Button href={setup_url} color={branding.primary_color}>
          Update Bank Account
        </Button>
      </Section>

      <Text
        className="text-[14px] leading-5 email-text"
        style={{ color: branding.tertiary_color }}
      >
        If you did not request this change, you can ignore this email. Your
        current account will remain active.
      </Text>
    </Layout>
  );
};

export default function AutopayUpdatePreview() {
  return (
    <AutopayUpdate
      branding={{
        company: "Dealer Capital Resources",
        logo_url: "https://example.com/logo.png",
        primary_color: "#006CFF",
        tertiary_color: "#9A9A9A",
        text_color: "#0f0f0f",
        background_color: "#f5f5f5",
        card_color: "#ffffff",
        border_color: "#e5e7eb",
        amount_bg_color: "#e5e7eb",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      customer_name="Goldey Homes LLC"
      setup_url="https://dcr.frappe.cloud/plaid-setup?customer=CUST-00001"
    />
  );
}
