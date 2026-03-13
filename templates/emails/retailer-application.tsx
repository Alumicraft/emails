import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface RetailerApplicationProps {
  branding: Branding;
  customer_name: string;
  dealer_license_no: string;
  factory_name: string;
}

export const RetailerApplication = ({
  branding,
  customer_name,
  dealer_license_no,
  factory_name,
}: RetailerApplicationProps) => {
  return (
    <Layout branding={branding} preview={`New dealer application for ${customer_name}`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        New Dealer Application
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Dealer Capital Resources is submitting the following dealer for your review and approval to order manufactured homes through your factory. Please find the required documents attached.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Dealer License No" value={dealer_license_no} />
        <InfoAmount branding={branding} label="Factory" value={factory_name} />
      </InfoCard>
    </Layout>
  );
};

export default function RetailerApplicationPreview() {
  return (
    <RetailerApplication
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
      dealer_license_no="DL-12345"
      factory_name="Champion Home Builders"
    />
  );
}
