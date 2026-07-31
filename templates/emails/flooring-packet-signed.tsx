import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface FlooringPacketSignedProps {
  branding: Branding;
  customer_name: string;
  loan_application: string;
  signed_date: string;
}

export const FlooringPacketSigned = ({
  branding,
  customer_name,
  loan_application,
  signed_date,
}: FlooringPacketSignedProps) => {
  return (
    <Layout branding={branding} preview="Your flooring packet has been fully executed">
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Flooring Packet Signed
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Your New Home Info Sheet, Exhibit A, and ACH Recurring Payment Authorization have been fully executed. A signed copy is attached for your records.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Loan Application" value={loan_application} />
        <InfoRow branding={branding} label="Signed Date" value={signed_date} />
        <InfoAmount branding={branding} label="Status" value="Fully Executed" />
      </InfoCard>
    </Layout>
  );
};

export default function FlooringPacketSignedPreview() {
  return (
    <FlooringPacketSigned
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
      signed_date="March 13, 2026"
    />
  );
}
