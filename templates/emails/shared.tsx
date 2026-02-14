import {
  Html,
  Head,
  Body,
  Container,
  Section,
  Img,
  Text,
  Link,
  Preview,
  Button as EmailButton,
  Row,
  Column,
  Hr,
  Tailwind,
} from "@react-email/components";
import * as React from "react";
import tailwindConfig from "../tailwind.config";

// ============================================================================
// HELPERS
// ============================================================================

export const toTitleCase = (str?: string): string => {
  if (!str) return "";
  return str
    .toLowerCase()
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

// ============================================================================
// INTERFACES
// ============================================================================

export interface Branding {
  company: string;
  logo_url?: string;
  logo_url_secondary?: string;
  logo_height?: number;
  logo_alt?: string;
  background_image_url?: string;
  primary_color: string;
  secondary_color?: string;
  tertiary_color?: string;
  text_color: string;
  background_color: string;
  primary_color_dark?: string;
  text_color_dark?: string;
  background_color_dark?: string;
  font_family: string;
  footer_text?: string;
  preheader?: string;
  website_url?: string;
  company_email?: string;
  company_phone?: string;
  mailing_address?: string;
  // Social URLs
  instagram_url?: string;
  tiktok_url?: string;
  facebook_url?: string;
  youtube_url?: string;
  twitter_url?: string;
  social_links?: Array<{ platform: string; url: string }>;
}

export interface Item {
  item_name: string;
  qty: number;
  rate?: string;
  amount?: string;
}

// ============================================================================
// BUTTON COMPONENT
// ============================================================================

export const Button = ({ href, color, children }: { href: string; color: string; children: React.ReactNode }) => (
  <EmailButton
    href={href}
    style={{
      backgroundColor: color,
      color: "#ffffff",
      display: "inline-block",
      padding: "12px 24px",
      borderRadius: "6px",
      fontWeight: 400,
      textDecoration: "none",
      border: "none",
    }}
  >
    {children}
  </EmailButton>
);

// ============================================================================
// SOCIAL ICONS
// ============================================================================

// Social icon names for icons8
const socialIconNames: Record<string, string> = {
  instagram: "instagram-new",
  tiktok: "tiktok--v1",
  facebook: "facebook--v1",
  youtube: "youtube-play",
  twitter: "x",
  x: "x",
};

const getSocialIconUrl = (platform: string, color: string): string => {
  const iconName = socialIconNames[platform.toLowerCase()] || "x";
  // Remove # from hex color
  const hexColor = color.replace("#", "");
  // ios-glyphs = solid filled icons without square backgrounds
  return `https://img.icons8.com/ios-glyphs/50/${hexColor}/${iconName}.png`;
};

// ============================================================================
// FOOTER COMPONENT
// ============================================================================

export const Footer = ({ branding }: { branding: Branding }) => {
  // Build social links array from individual URLs if social_links not provided
  // Order: instagram, tiktok, facebook, youtube, x
  const socialLinks = branding.social_links?.length
    ? branding.social_links
    : [
        branding.instagram_url && { platform: "instagram", url: branding.instagram_url },
        branding.tiktok_url && { platform: "tiktok", url: branding.tiktok_url },
        branding.facebook_url && { platform: "facebook", url: branding.facebook_url },
        branding.youtube_url && { platform: "youtube", url: branding.youtube_url },
        branding.twitter_url && { platform: "twitter", url: branding.twitter_url },
      ].filter(Boolean) as Array<{ platform: string; url: string }>;

  const footerLogo = branding.logo_url_secondary || branding.logo_url;
  const tertiaryColor = branding.tertiary_color || "#6b7280";

  return (
    <Section className="mt-12 mb-8">
      {/* Divider line */}
      <Hr className="mb-8" style={{ border: "none", borderTop: `1px solid ${tertiaryColor}`, marginTop: 0 }} />
      {/* Logo */}
      {footerLogo && (
        <Img
          alt={branding.logo_alt || branding.company}
          height="24"
          src={footerLogo}
          className="mb-6"
        />
      )}

      {/* Social Links */}
      {socialLinks.length > 0 && (
        <table cellPadding="0" cellSpacing="0" className="mb-4">
          <tr>
            {socialLinks.map((social, index) => (
              <td key={index} className={index === 0 ? "" : "pl-2"}>
                <Link href={social.url}>
                  <Img
                    alt={social.platform}
                    height="20"
                    width="20"
                    src={getSocialIconUrl(social.platform, "000000")}
                  />
                </Link>
              </td>
            ))}
          </tr>
        </table>
      )}

      {/* Address */}
      {branding.mailing_address && (
        <Text style={{ margin: "0 0 4px 0", fontSize: "14px", color: tertiaryColor, lineHeight: "20px" }}>
          {branding.mailing_address}
        </Text>
      )}

      {/* Contact */}
      {(branding.company_email || branding.company_phone) && (
        <Text style={{ margin: "0", fontSize: "14px", color: tertiaryColor, lineHeight: "20px" }}>
          {branding.company_email && (
            <Link
              href={`mailto:${branding.company_email}`}
              style={{ color: tertiaryColor, textDecoration: "none" }}
            >
              {branding.company_email}
            </Link>
          )}
          {branding.company_email && branding.company_phone && " | "}
          {branding.company_phone && (
            <Link
              href={`tel:${branding.company_phone.replace(/[^+\d]/g, "")}`}
              style={{ color: tertiaryColor, textDecoration: "none" }}
            >
              {branding.company_phone}
            </Link>
          )}
        </Text>
      )}
    </Section>
  );
};

// ============================================================================
// CONFIDENTIALITY COMPONENT
// ============================================================================

export const Confidentiality = () => (
  <Text className="email-confidentiality" style={{
    fontSize: "11px",
    lineHeight: "16px",
    color: "#9ca3af",
    textAlign: "center",
    margin: "24px 0 0 0",
  }}>
    This email and any attachments are confidential and intended solely for the recipient. If you received this in error, please delete it and notify the sender.
  </Text>
);

// ============================================================================
// LAYOUT COMPONENT
// ============================================================================

export const Layout = ({
  branding,
  preview,
  children,
}: {
  branding: Branding;
  preview?: string;
  children: React.ReactNode;
}) => {
  const darkBg = branding.background_color_dark || "#1a1a1a";
  const darkText = branding.text_color_dark || "#ffffff";

  const darkModeStyles = `
    @media (prefers-color-scheme: dark) {
      .email-body { background-color: ${darkBg} !important; }
      .email-card { background-color: #2d2d2d !important; }
      .email-heading, .email-text { color: ${darkText} !important; }
      .email-row-label { color: #e5e7eb !important; }
      .email-row-value { color: #d1d5db !important; }
      .email-divider { border-color: #4b5563 !important; }
      .email-confidentiality { color: #6b7280 !important; }
    }
  `;

  return (
    <Html lang="en">
      <Head>
        <meta name="color-scheme" content="light dark" />
        <meta name="supported-color-schemes" content="light dark" />
        <style dangerouslySetInnerHTML={{ __html: darkModeStyles }} />
      </Head>
      {preview && <Preview>{preview}</Preview>}
      <Tailwind config={tailwindConfig}>
        <Body
          className="mx-auto my-0 font-sans email-body"
          style={{
            fontFamily: branding.font_family,
            backgroundColor: branding.background_color,
          }}
        >
          <Container className="mx-auto my-0 pt-6 pb-8 max-w-[600px]">
            <Section
              className="px-6 py-8 email-card"
              style={{
                backgroundColor: "#ffffff",
              }}
            >
              {branding.logo_url && (
                <Img
                  src={branding.logo_url}
                  height={branding.logo_height || 48}
                  alt={branding.logo_alt || branding.company}
                  className="mt-4 mb-8"
                />
              )}

              {children}

              <Footer branding={branding} />
            </Section>
            <Confidentiality />
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

// ============================================================================
// INFO CARD COMPONENTS
// ============================================================================

const monoFont = "Courier, monospace";

export const InfoCard = ({ children }: { children: React.ReactNode }) => (
  <table cellPadding="0" cellSpacing="0" style={{
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "32px",
    marginBottom: "32px"
  }}>
    <tbody>
      {children}
    </tbody>
  </table>
);

export const InfoRow = ({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) => (
  <tr>
    <td className="email-row-label email-divider" style={{
      padding: "8px 0",
      borderBottom: "1px solid #e5e7eb",
      color: "#1f2937",
      fontSize: "14px",
      fontWeight: 500,
      whiteSpace: "nowrap",
      paddingRight: "16px"
    }}>{label}</td>
    <td className="email-row-value email-divider" style={{
      padding: "8px 0",
      borderBottom: "1px solid #e5e7eb",
      color: valueColor || "#1f2937",
      fontSize: "14px",
      fontFamily: monoFont
    }}>{value}</td>
  </tr>
);

export const InfoAmount = ({ label, value }: { label: string; value: string }) => (
  <tr>
    <td className="email-row-label" style={{
      padding: "8px 0",
      color: "#1f2937",
      fontSize: "14px",
      fontWeight: 500,
      whiteSpace: "nowrap",
      paddingRight: "16px"
    }}>{label}</td>
    <td className="email-row-value" style={{
      padding: "8px 0",
      color: "#1f2937",
      fontSize: "14px",
      fontFamily: monoFont
    }}>{value}</td>
  </tr>
);
