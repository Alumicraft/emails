import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface FlooringPacketSentProps {
  branding: Branding;
  customer_name: string;
  loan_application: string;
  requested_advance_amount: string;
  factory_name: string;
}

export const FlooringPacketSent = ({
  branding,
  customer_name,
  loan_application,
  requested_advance_amount,
  factory_name,
}: FlooringPacketSentProps) => {
  return (
    <Layout branding={branding} preview="Your flooring packet is ready for signature">
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Flooring Packet
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Your Exhibit A and ACH Approval documents are ready for review and signature. You will receive a separate email from DocuSign with the signing link.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Loan Application" value={loan_application} />
        <InfoRow branding={branding} label="Advance Amount" value={`$${requested_advance_amount}`} />
        <InfoAmount branding={branding} label="Factory" value={factory_name} />
      </InfoCard>
    </Layout>
  );
};

export default function FlooringPacketSentPreview() {
  return (
    <FlooringPacketSent
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
      loan_application="LA-2026-001"
      requested_advance_amount="85,000.00"
      factory_name="Champion Home Builders"
    />
  );
}
