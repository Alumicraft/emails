import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, Branding } from "./shared";

export { Branding } from "./shared";

export interface AutopayConnectedProps {
  branding: Branding;
  customer_name: string;
  bank_name: string;
  account_last4: string;
}

export const AutopayConnected = ({
  branding,
  customer_name,
  bank_name,
  account_last4,
}: AutopayConnectedProps) => {
  return (
    <Layout branding={branding} preview="Your bank account is now connected for auto-pay">
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Auto-Pay Connected
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Hi {customer_name}, your bank account ({bank_name} ending in {account_last4}) has been
        successfully connected for automatic loan payments.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Bank Account" value={`${bank_name} ****${account_last4}`} />
      </InfoCard>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Payments will be debited automatically per your loan terms. You will receive advance
        notification before each debit.
      </Text>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        If you have any questions or need to update your bank account, please contact us at{" "}
        {branding.company_email || branding.company_phone
          ? [branding.company_email, branding.company_phone].filter(Boolean).join(" or ")
          : "your account representative"}
        .
      </Text>
    </Layout>
  );
};

export default function AutopayConnectedPreview() {
  return (
    <AutopayConnected
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
        company_email: "support@dealercapital.net",
        company_phone: "(555) 123-4567",
      }}
      customer_name="ABC Homes"
      bank_name="Chase"
      account_last4="5678"
    />
  );
}
