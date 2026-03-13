import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface AchPaymentFailureProps {
  branding: Branding;
  loan: string;
  customer_name: string;
  scheduled_date: string;
  failure_reason: string;
  amount: string;
}

export const AchPaymentFailure = ({
  branding,
  loan,
  customer_name,
  scheduled_date,
  failure_reason,
  amount,
}: AchPaymentFailureProps) => {
  return (
    <Layout branding={branding} preview={`Payment of $${amount} could not be processed`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Payment Failed
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Your scheduled payment could not be processed. Please contact us to resolve this issue.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Loan" value={loan} />
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Scheduled Date" value={scheduled_date} />
        <InfoRow branding={branding} label="Reason" value={failure_reason} />
        <InfoAmount branding={branding} label="Amount" value={`$${amount}`} />
      </InfoCard>
    </Layout>
  );
};

export default function AchPaymentFailurePreview() {
  return (
    <AchPaymentFailure
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
      loan="LOAN-2026-001"
      customer_name="ABC Homes"
      scheduled_date="March 15, 2026"
      failure_reason="Insufficient funds"
      amount="2,500.00"
    />
  );
}
