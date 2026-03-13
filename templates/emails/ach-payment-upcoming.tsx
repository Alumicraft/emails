import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface AchPaymentUpcomingProps {
  branding: Branding;
  loan: string;
  customer_name: string;
  scheduled_date: string;
  amount: string;
  account_last4: string;
}

export const AchPaymentUpcoming = ({
  branding,
  loan,
  customer_name,
  scheduled_date,
  amount,
  account_last4,
}: AchPaymentUpcomingProps) => {
  return (
    <Layout branding={branding} preview={`Upcoming payment of $${amount} on ${scheduled_date}`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Upcoming Payment
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Your scheduled payment will be debited from your account ending in {account_last4} on the date below.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Loan" value={loan} />
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Debit Date" value={scheduled_date} />
        <InfoAmount branding={branding} label="Amount" value={`$${amount}`} />
      </InfoCard>
    </Layout>
  );
};

export default function AchPaymentUpcomingPreview() {
  return (
    <AchPaymentUpcoming
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
      amount="2,500.00"
      account_last4="4321"
    />
  );
}
