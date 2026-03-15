import { Heading, Text, Section, Button } from "@react-email/components";
import { Layout, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface EmailVerificationEmailProps {
  branding: Branding;
  verification_link: string;
  user_name?: string;
  expiry_time?: string;
}

export const EmailVerificationEmail = ({
  branding,
  verification_link,
  user_name,
  expiry_time = "24 hours",
}: EmailVerificationEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="email-heading"
        style={{ color: branding.text_color, marginTop: 0, fontSize: "24px", fontWeight: 500, lineHeight: "32px" }}
      >
        {user_name ? `Hello ${toTitleCase(user_name)},` : "Verify your email"}
      </Heading>

      <Text
        className="email-text"
        style={{ color: branding.text_color, fontSize: "15px", lineHeight: "24px" }}
      >
        Click the button below to verify your email.
      </Text>

      <Section style={{ marginTop: "32px", marginBottom: "32px" }}>
        <Button
          className="email-button"
          style={{
            backgroundColor: branding.primary_color,
            color: branding.button_text_color || "#ffffff",
            display: "inline-block",
            boxSizing: "border-box" as const,
            width: "100%",
            borderRadius: "4px",
            padding: "12px",
            textAlign: "center" as const,
            fontWeight: 500,
            fontSize: "16px",
            lineHeight: "1.2",
            textDecoration: "none",
            border: "none",
          }}
          href={verification_link}
        >
          Verify Email
        </Button>
      </Section>

      <Text
        style={{ color: branding.tertiary_color, fontSize: "12px", lineHeight: "24px" }}
      >
        This link will expire in {expiry_time}.
        <br /><br />
        If you didn't create an account, you can safely ignore this email.
      </Text>
    </Layout>
  );
};

// Preview with sample data
export default function EmailVerificationEmailPreview() {
  return (
    <EmailVerificationEmail
      branding={{
        company: "Alumicraft",
        logo_url: "https://example.com/logo.png",
        primary_color: "#006CFF",
        tertiary_color: "#9A9A9A",
        text_color: "#0f0f0f",
        background_color: "#f5f5f5",
        card_color: "#ffffff",
        border_color: "#e5e7eb",
        amount_bg_color: "#e5e7eb",
        primary_color_dark: "#4D8DFF",
        tertiary_color_dark: "#6B7280",
        text_color_dark: "#E5E7EB",
        background_color_dark: "#E5E7EB",
        card_color_dark: "#000000",
        border_color_dark: "#4b5563",
        amount_bg_color_dark: "#374151",
        font_family: "Arial, Helvetica, sans-serif",
      }}
      verification_link="https://example.com/verify?token=abc123"
      user_name="John"
    />
  );
}
