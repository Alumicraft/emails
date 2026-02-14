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
  const darkBorder = branding.border_color_dark || "#4b5563";
  const darkHighlight = branding.highlight_color_dark || "#374151";
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
      .email-social-light { display: none !important; }
      .email-social-dark { display: inline-block !important; }
      .email-footer-text { color: ${tertiaryColorDark} !important; }
      .email-footer-link { color: ${tertiaryColorDark} !important; }
      .email-footer-divider { border-color: ${darkBorder} !important; }
      .email-info-card { background-color: ${darkBg} !important; }
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
          className="mx-auto my-0 font-sans email-body"
          style={{
            fontFamily: branding.font_family,
            backgroundColor: branding.background_color,
          }}
        >
          <Container
            className="mx-auto my-0 pt-5 px-6 pb-12 max-w-[600px]"
          >
            <Section
              className="mt-8 p-8 email-card"
              style={{
                backgroundColor: branding.card_color || "#ffffff",
                borderRadius: "4px",
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
                  className="mt-4 mb-8"
                />
              )}
              <Heading
                className="text-[24px] font-medium email-heading"
                style={{ color: branding.text_color }}
              >
                {user_name ? `Hello ${toTitleCase(user_name)}, sign in.` : "Sign in"}
              </Heading>
              <Text
                className="text-[15px] leading-6 email-text"
                style={{ color: branding.text_color }}
              >
                Click the button below to sign in.
              </Text>
              <Section className="my-8">
                <Button
                  className="email-button box-border w-full rounded-[4px] px-[12px] py-[12px] text-center font-medium text-[16px]"
                  style={{ backgroundColor: branding.primary_color, color: branding.button_text_color || "#ffffff" }}
                  href={magic_link}
                >
                  Login
                </Button>
              </Section>
              <Text className="text-[12px]" style={{ color: branding.tertiary_color || "#6b7280" }}>
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
        primary_color: "#4f46e5",
        tertiary_color: "#6b7280",
        text_color: "#1f2937",
        background_color: "#f3f4f6",
        font_family: "Arial, Helvetica, sans-serif",
        website_url: "https://acme.com",
        mailing_address: "123 Main Street, San Francisco, CA 94102",
        company_email: "hello@acme.com",
        company_phone: "+1 (555) 123-4567",
        instagram_url: "https://instagram.com/acme",
        tiktok_url: "https://tiktok.com/@acme",
        facebook_url: "https://facebook.com/acme",
        youtube_url: "https://youtube.com/acme",
        twitter_url: "https://twitter.com/acme",
      }}
      user_name="John"
      magic_link="https://acme.com/auth/verify?token=abc123xyz"
      expiry_time="15 minutes"
    />
  );
}
