import { Heading, Text, Section } from "@react-email/components";
import { Layout, Button, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface DealerWelcomeProps {
  branding: Branding;
  customer_name: string;
  dcr_account_no: string;
  portal_url?: string;
}

export const DealerWelcome = ({
  branding,
  customer_name,
  dcr_account_no,
  portal_url,
}: DealerWelcomeProps) => {
  return (
    <Layout branding={branding} preview={`Welcome to Dealer Capital Resources, ${customer_name}`}>
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Welcome to DCR
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Your dealer account has been approved. Below are your account details.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="DCR Account No" value={dcr_account_no} />
        <InfoAmount branding={branding} label="Status" value="Approved" />
      </InfoCard>

      {portal_url && (
        <Section style={{ textAlign: "center", marginTop: "8px", marginBottom: "24px" }}>
          <Button href={portal_url} color={branding.primary_color} textColor={branding.button_text_color}>
            Open Dealer Portal
          </Button>
        </Section>
      )}
    </Layout>
  );
};

export default function DealerWelcomePreview() {
  return (
    <DealerWelcome
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
      dcr_account_no="DCR-001234"
      portal_url="https://example.com/portal"
    />
  );
}
