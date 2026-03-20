import { Heading, Text } from "@react-email/components";
import { Layout, InfoCard, InfoRow, InfoAmount, Branding } from "./shared";

export { Branding } from "./shared";

export interface PreApprovalProps {
  branding: Branding;
  customer_name: string;
  loan_application: string;
  loan_amount: string;
}

export const PreApproval = ({
  branding,
  customer_name,
  loan_application,
  loan_amount,
}: PreApprovalProps) => {
  return (
    <Layout branding={branding} preview="Your Advance Pre-Approval letter is attached">
      <Heading
        className="text-[24px] font-medium email-heading"
        style={{ color: branding.text_color, marginTop: 0 }}
      >
        Advance Pre-Approval
      </Heading>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        Please find attached your Advance Pre-Approval letter for your review. This letter confirms that your flooring application has been pre-approved.
      </Text>

      <InfoCard branding={branding}>
        <InfoRow branding={branding} label="Dealer" value={customer_name} />
        <InfoRow branding={branding} label="Application" value={loan_application} />
        {loan_amount && (
          <InfoAmount branding={branding} label="Pre-Approved Amount" value={`$${loan_amount}`} />
        )}
      </InfoCard>

      <Text
        className="text-[15px] leading-6 email-text"
        style={{ color: branding.text_color }}
      >
        If you have any questions, please don't hesitate to contact us.
      </Text>
    </Layout>
  );
};

export default function PreApprovalPreview() {
  return (
    <PreApproval
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
      loan_application="ACC-LOAP-2026-00001"
      loan_amount="150,000"
    />
  );
}
