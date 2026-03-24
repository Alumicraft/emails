import { Heading, Text, Section } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Button, Branding } from "./shared";

export { Branding } from "./shared";

export interface AutopaySetupProps {
  branding: Branding;
  customer_name: string;
  loan_name: string;
  loan_amount: string;
  setup_url: string;
}

export const AutopaySetup = ({
  branding,
  customer_name,
  loan_name,
  loan_amount,
  setup_url,
}: AutopaySetupProps) => {
  return (
    <Layout branding={branding} preview={`Set up auto-pay for Loan ${loan_name}`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Set Up Auto-Pay
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Your loan has been created. Please connect your bank account to enable automatic payments.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Loan" value={loan_name} />
        <InfoAmount branding={branding} label="Loan Amount" value={`$${loan_amount}`} />
      </InfoCard>

      <Section className="my-8 text-center">
        <Button
          href={setup_url}
          color={branding.primary_color}
          textColor={branding.button_text_color}
        >
          Connect Bank Account
        </Button>
      </Section>
    </Layout>
  );
};

export default function AutopaySetupPreview() {
  return (
    <AutopaySetup
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
      loan_name="LOAN-2026-001"
      loan_amount="355,000.00"
      setup_url="https://example.com/plaid-setup?loan=LOAN-2026-001"
    />
  );
}
