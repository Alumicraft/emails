import { Heading, Text, Section } from "@react-email/components";
import { Layout, Button, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface DealerAgreementSentProps {
  branding: Branding;
  customer_name: string;
  email: string;
  signing_url: string;
}

export const DealerAgreementSent = ({
  branding,
  customer_name,
  email,
  signing_url,
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
        Your Dealer Agreement is ready for review and signature. Click the button below to sign your document.
      </Text>

      <Section style={{ textAlign: "center", marginTop: "24px", marginBottom: "8px" }}>
        <Button href={signing_url} color={branding.primary_color} textColor={branding.button_text_color}>
          Sign Document
        </Button>
      </Section>

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
      signing_url="https://example.com/sign"
    />
  );
}
