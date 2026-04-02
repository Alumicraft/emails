import { Heading, Text, Section } from "@react-email/components";
import { Layout, Button, Branding, toTitleCase } from "./shared";

export { Branding } from "./shared";

export interface WelcomeEmailProps {
  branding: Branding;
  user_name?: string;
  login_link?: string;
  custom_message?: string;
}

export const WelcomeEmail = ({
  branding,
  user_name,
  login_link,
  custom_message,
}: WelcomeEmailProps) => {
  return (
    <Layout branding={branding}>
      <Heading
        className="email-heading"
        style={{ color: branding.text_color, marginTop: 0, fontSize: "24px", fontWeight: 500, lineHeight: "32px" }}
      >
        Your account is ready{user_name ? `, ${toTitleCase(user_name)}` : ""}!
      </Heading>

      <Text
        className="email-text"
        style={{ color: branding.text_color, fontSize: "15px", lineHeight: "24px" }}
      >
        {custom_message || "Log in to access company resources."}
      </Text>

      {login_link && (
        <Section style={{ marginTop: "32px", marginBottom: "32px" }}>
          <Button
            href={login_link}
            color={branding.primary_color}
            textColor={branding.button_text_color}
          >
            Log In
          </Button>
        </Section>
      )}
    </Layout>
  );
};

// Preview with sample data
export default function WelcomeEmailPreview() {
  return (
    <WelcomeEmail
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
      user_name="John"
      login_link="https://example.com/login"
    />
  );
}
