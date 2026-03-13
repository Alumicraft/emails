import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface FactoryLoaReceivedProps {
  branding: Branding;
  customer_name: string;
  factory_name: string;
  loa_date: string;
}

export const FactoryLoaReceived = ({
  branding,
  customer_name,
  factory_name,
  loa_date,
}: FactoryLoaReceivedProps) => {
  return (
    <Layout branding={branding} preview={`You have been approved to order through ${factory_name}`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Factory Approved
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        You have been approved to order manufactured homes through the factory below.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Factory" value={factory_name} />
        <InfoRow branding={branding} label="Approval Date" value={loa_date} />
        <InfoAmount branding={branding} label="Status" value="Approved" />
      </InfoCard>
    </Layout>
  );
};

export default function FactoryLoaReceivedPreview() {
  return (
    <FactoryLoaReceived
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
      loa_date="March 13, 2026"
    />
  );
}
