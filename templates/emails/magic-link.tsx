import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Section,
  Tailwind,
  Text,
} from "@react-email/components";
import tailwindConfig from "../tailwind.config";
import { Footer, Confidentiality, Logo, Branding, toTitleCase } from "./shared";

export interface MagicLinkEmailProps {
  branding: Branding;
  magic_link: string;
  user_name?: string;
  expiry_time?: string;
}

export const MagicLinkEmail = ({
  branding,
  magic_link,
  user_name,
  expiry_time = "15 minutes",
}: MagicLinkEmailProps) => {
  const darkBg = branding.background_color_dark || "#1a1a1a";
  const darkCard = branding.card_color_dark || "#000000";
  const darkTable = branding.table_color_dark || darkBg;
  const darkBorder = branding.border_color_dark || "#4b5563";
  const darkHighlight = branding.amount_bg_color_dark || "#374151";
  const darkText = branding.text_color_dark || "#ffffff";
  const buttonTextColorDark = branding.button_text_color_dark || branding.button_text_color || "#ffffff";
  const tertiaryColorDark = branding.tertiary_color_dark || "#9ca3af";

  const darkModeStyles = `
    @media (prefers-color-scheme: dark) {
      .email-body { background-color: ${darkBg} !important; }
      .email-card { background-color: ${darkCard} !important; }
      .email-heading, .email-text { color: ${darkText} !important; }
      .email-row-label { color: #e5e7eb !important; }
      .email-row-value { color: #d1d5db !important; }
      .email-divider { border-color: ${darkBorder} !important; }
      .email-confidentiality { color: #6b7280 !important; }
      .email-button { color: ${buttonTextColorDark} !important; }
      .email-logo-light { display: none !important; }
      .email-logo-dark { display: block !important; }
      .email-footer-text { color: ${tertiaryColorDark} !important; }
      .email-footer-link { color: ${tertiaryColorDark} !important; }
      .email-footer-divider { border-color: ${darkBorder} !important; }
      .email-info-card { background-color: ${darkTable} !important; }
      .email-amount-bg { background-color: ${darkHighlight} !important; }
    }
  `;

  return (
    <Html lang="en">
      <Head>
        <meta name="color-scheme" content="light dark" />
        <meta name="supported-color-schemes" content="light dark" />
        <style dangerouslySetInnerHTML={{ __html: darkModeStyles }} />
      </Head>
      <Preview>Sign in to {branding.company} with this magic link</Preview>
      <Tailwind config={tailwindConfig}>
        <Body
          className="email-body"
          style={{
            margin: "0 auto",
            padding: 0,
            fontFamily: branding.font_family,
            backgroundColor: branding.background_color,
            WebkitTextSizeAdjust: "100%",
            msTextSizeAdjust: "100%",
          }}
        >
          <Container
            style={{ margin: "0 auto", paddingTop: "20px", paddingLeft: "24px", paddingRight: "24px", paddingBottom: "48px", maxWidth: "600px" }}
          >
            <Section
              className="email-card"
              style={{
                marginTop: "32px",
                padding: "32px",
                backgroundColor: branding.card_color || "#ffffff",
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                backgroundImage: branding.background_image_url
                  ? `linear-gradient(rgba(255,255,255,0.75), rgba(255,255,255,0.75)), url(${branding.background_image_url})`
                  : undefined,
                backgroundSize: "cover",
                backgroundPosition: "center",
              }}
            >
              {branding.logo_url && (
                <Logo
                  lightSrc={branding.logo_url}
                  darkSrc={branding.logo_url_dark}
                  alt={branding.logo_alt || branding.company}
                  height={branding.logo_height || 48}
                  style={{ marginTop: "16px", marginBottom: "32px" }}
                />
              )}
              <Heading
                className="email-heading"
                style={{ color: branding.text_color, fontSize: "24px", fontWeight: 500, lineHeight: "32px" }}
              >
                {user_name ? `Hello ${toTitleCase(user_name)}, sign in.` : "Sign in"}
              </Heading>
              <Text
                className="email-text"
                style={{ color: branding.text_color, fontSize: "15px", lineHeight: "24px" }}
              >
                Click the button below to sign in.
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
                  href={magic_link}
                >
                  Login
                </Button>
              </Section>
              <Text style={{ color: branding.tertiary_color || "#6b7280", fontSize: "12px", lineHeight: "18px" }}>
                This link will expire in {expiry_time}.
                <br /><br />
                If you didn't try to login, you can safely ignore this email.
              </Text>

              {/* Footer */}
              <Footer branding={branding} />
            </Section>
            <Confidentiality />
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

// Preview with sample data
export default function MagicLinkEmailPreview() {
  return (
    <MagicLinkEmail
      branding={{
        company: "Acme Inc",
        logo_url: "https://react-email-demo-ijnnx5hul-resend.vercel.app/static/vercel-logo.png",
        logo_url_secondary: "https://react-email-demo-ijnnx5hul-resend.vercel.app/static/vercel-logo.png",
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
        website_url: "https://acme.com",
        mailing_address: "123 Main Street, San Francisco, CA 94102",
        company_email: "hello@acme.com",
        company_phone: "+1 (555) 123-4567",
      }}
      user_name="John"
      magic_link="https://acme.com/auth/verify?token=abc123xyz"
      expiry_time="15 minutes"
    />
  );
}
