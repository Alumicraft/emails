import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface LoanDisbursedProps {
  branding: Branding;
  customer_name: string;
  factory_name: string;
  loan: string;
  home_build_request: string;
  amount: string;
}

export const LoanDisbursed = ({
  branding,
  customer_name,
  factory_name,
  loan,
  home_build_request,
  amount,
}: LoanDisbursedProps) => {
  return (
    <Layout branding={branding} preview={`Advance of $${amount} disbursed to ${factory_name}`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Advance Disbursed
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        The advance for your home build has been sent to the factory on your behalf.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Factory" value={factory_name} />
        <InfoRow branding={branding} label="Loan" value={loan} />
        <InfoRow branding={branding} label="Home Build" value={home_build_request} />
        <InfoAmount branding={branding} label="Amount Advanced" value={`$${amount}`} />
      </InfoCard>
    </Layout>
  );
};

export default function LoanDisbursedPreview() {
  return (
    <LoanDisbursed
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
      factory_name="Champion Home Builders"
      loan="LOAN-2026-001"
      home_build_request="HBR-2026-001"
      amount="85,000.00"
    />
  );
}
