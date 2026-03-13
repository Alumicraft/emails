import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface DealerAgreementSentProps {
  branding: Branding;
  customer_name: string;
  email: string;
}

export const DealerAgreementSent = ({
  branding,
  customer_name,
  email,
}: DealerAgreementSentProps) => {
  return (
    <Layout branding={branding} preview="Your Dealer Agreement is ready for signature">
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Dealer Agreement
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Your Dealer Agreement is ready for review and signature. You will receive a separate email from DocuSign with the signing link.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Sent To" value={email} />
        <InfoAmount branding={branding} label="Document" value="Dealer Agreement" />
      </InfoCard>
    </Layout>
  );
};

export default function DealerAgreementSentPreview() {
  return (
    <DealerAgreementSent
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
      email="dealer@abchomes.com"
    />
  );
}
