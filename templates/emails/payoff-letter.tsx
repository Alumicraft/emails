import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, Branding } from "./shared";

export { Branding } from "./shared";

export interface PayoffLetterProps {
  branding: Branding;
  customer_name: string;
  loan: string;
  payoff_type: string;
}

export const PayoffLetter = ({
  branding,
  customer_name,
  loan,
  payoff_type,
}: PayoffLetterProps) => {
  return (
    <Layout branding={branding} preview={`${payoff_type} payoff letter attached`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Loan Payoff Letter
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Please find attached your payoff letter for the loan below.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Loan" value={loan} />
        <InfoRow branding={branding} label="Payoff Type" value={payoff_type} />
      </InfoCard>
    </Layout>
  );
};

export default function PayoffLetterPreview() {
  return (
    <PayoffLetter
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
      loan="ACC-LOAN-2026-00001"
      payoff_type="Flooring"
    />
  );
}
