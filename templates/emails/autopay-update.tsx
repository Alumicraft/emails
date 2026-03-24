import { Heading, Text, Section } from "@react-email/components";
import { Layout, Button, Branding } from "./shared";

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
    <Layout branding={branding} preview="Update your auto-pay bank account">
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Update Auto-Pay
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Hi {customer_name}, please update your bank account for automatic payments by clicking the button below.
      </Text>

      <Section className="my-8 text-center">
        <Button
          href={setup_url}
          color={branding.primary_color}
          textColor={branding.button_text_color}
        >
          Update Bank Account
        </Button>
      </Section>
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
      customer_name="ABC Homes"
      setup_url="https://example.com/plaid-setup?customer=ABC-001"
    />
  );
}
