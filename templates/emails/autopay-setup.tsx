import { Heading, Text } from "@react-email/components";
import { Layout, Button, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

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
    <Layout branding={branding} preview={`Set up Auto-Pay for loan ${loan_name}`}>
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
        A new flooring loan has been created. Connect your business bank account
        to enable automatic payments.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Loan" value={loan_name} />
        <InfoAmount branding={branding} label="Loan Amount" value={`$${loan_amount}`} />
      </InfoCard>

      <Section style={{ textAlign: "center" as const, marginTop: "24px", marginBottom: "24px" }}>
        <Button href={setup_url} color={branding.primary_color}>
          Connect Bank Account
        </Button>
      </Section>

      <Text
        className="text-[14px] leading-5 email-text"
        style={{ color: branding.tertiary_color }}
      >
        Payments will not begin until a bank account is connected. Once
        connected, this account will also be used for any future loans unless
        you set up a different account.
      </Text>
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
      customer_name="Goldey Homes LLC"
      loan_name="LOAN-2026-001"
      loan_amount="85,000.00"
      setup_url="https://dcr.frappe.cloud/plaid-setup?loan=LOAN-2026-001"
    />
  );
}
