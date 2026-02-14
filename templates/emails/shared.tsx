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
  logo_url_dark?: string;
  logo_url_secondary?: string;
  logo_url_secondary_dark?: string;
  logo_height?: number;
  logo_alt?: string;
  background_image_url?: string;
  primary_color: string;
  secondary_color?: string;
  tertiary_color?: string;
  text_color: string;
  background_color: string;
  card_color?: string;
  border_color?: string;
  highlight_color?: string;
  button_text_color?: string;
  primary_color_dark?: string;
  card_color_dark?: string;
  border_color_dark?: string;
  highlight_color_dark?: string;
  secondary_color_dark?: string;
  tertiary_color_dark?: string;
  text_color_dark?: string;
  background_color_dark?: string;
  button_text_color_dark?: string;
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

export const Button = ({ href, color, textColor, children }: { href: string; color: string; textColor?: string; children: React.ReactNode }) => (
  <EmailButton
    href={href}
    className="email-button"
    style={{
      backgroundColor: color,
      color: textColor || "#ffffff",
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
// LOGO COMPONENT (dark mode swap via CSS show/hide)
// ============================================================================

export const Logo = ({
  lightSrc,
  darkSrc,
  alt,
  height,
  className,
}: {
  lightSrc: string;
  darkSrc?: string;
  alt: string;
  height: string | number;
  className?: string;
}) => {
  if (!darkSrc) {
    return <Img src={lightSrc} height={height} alt={alt} className={className} />;
  }
  return (
    <>
      <Img src={lightSrc} height={height} alt={alt} className={`email-logo-light ${className || ""}`} />
      <Img src={darkSrc} height={height} alt={alt} className={`email-logo-dark ${className || ""}`} style={{ display: "none" }} />
    </>
  );
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
  const footerLogoDark = branding.logo_url_secondary_dark || branding.logo_url_dark;
  const tertiaryColor = branding.tertiary_color || "#6b7280";
  const tertiaryColorDark = branding.tertiary_color_dark || "#9ca3af";
  const iconColor = "000000";
  const iconColorDark = tertiaryColorDark.replace("#", "");

  return (
    <Section className="mt-12 mb-8">
      {/* Divider line */}
      <Hr className="email-footer-divider mb-8" style={{ border: "none", borderTop: `1px solid ${tertiaryColor}`, marginTop: 0 }} />
      {/* Logo */}
      {footerLogo && (
        <Logo
          lightSrc={footerLogo}
          darkSrc={footerLogoDark}
          alt={branding.logo_alt || branding.company}
          height="24"
          className="mb-6"
        />
      )}

      {/* Social Links — light mode icons */}
      {socialLinks.length > 0 && (
        <table cellPadding="0" cellSpacing="0" className="email-social-light mb-4">
          <tr>
            {socialLinks.map((social, index) => (
              <td key={index} className={index === 0 ? "" : "pl-2"}>
                <Link href={social.url}>
                  <Img
                    alt={social.platform}
                    height="20"
                    width="20"
                    src={getSocialIconUrl(social.platform, iconColor)}
                  />
                </Link>
              </td>
            ))}
          </tr>
        </table>
      )}

      {/* Social Links — dark mode icons (hidden by default, shown via CSS) */}
      {socialLinks.length > 0 && (
        <table cellPadding="0" cellSpacing="0" className="email-social-dark mb-4" style={{ display: "none" }}>
          <tr>
            {socialLinks.map((social, index) => (
              <td key={index} className={index === 0 ? "" : "pl-2"}>
                <Link href={social.url}>
                  <Img
                    alt={social.platform}
                    height="20"
                    width="20"
                    src={getSocialIconUrl(social.platform, iconColorDark)}
                  />
                </Link>
              </td>
            ))}
          </tr>
        </table>
      )}

      {/* Address */}
      {branding.mailing_address && (
        <Text className="email-footer-text" style={{ margin: "0 0 4px 0", fontSize: "14px", color: tertiaryColor, lineHeight: "20px" }}>
          {branding.mailing_address}
        </Text>
      )}

      {/* Contact */}
      {(branding.company_email || branding.company_phone) && (
        <Text className="email-footer-text" style={{ margin: "0", fontSize: "14px", color: tertiaryColor, lineHeight: "20px" }}>
          {branding.company_email && (
            <Link
              href={`mailto:${branding.company_email}`}
              className="email-footer-link"
              style={{ color: tertiaryColor, textDecoration: "none" }}
            >
              {branding.company_email}
            </Link>
          )}
          {branding.company_email && branding.company_phone && " | "}
          {branding.company_phone && (
            <Link
              href={`tel:${branding.company_phone.replace(/[^+\d]/g, "")}`}
              className="email-footer-link"
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
                backgroundColor: branding.card_color || "#ffffff",
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

export const InfoCard = ({ branding, children }: { branding: Branding; children: React.ReactNode }) => (
  <table cellPadding="0" cellSpacing="0" className="email-info-card" style={{
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "32px",
    marginBottom: "32px",
    backgroundColor: branding.background_color,
    borderRadius: "6px",
    overflow: "hidden",
  }}>
    <tbody>
      {children}
    </tbody>
  </table>
);

export const InfoRow = ({ branding, label, value, valueColor }: { branding: Branding; label: string; value: string; valueColor?: string }) => (
  <tr>
    <td className="email-row-label email-divider" style={{
      padding: "12px 16px",
      borderBottom: `1px solid ${branding.border_color || "#e5e7eb"}`,
      color: branding.secondary_color || "#6b7280",
      fontSize: "14px",
      fontWeight: 400,
      whiteSpace: "nowrap",
    }}>{label}</td>
    <td className="email-row-value email-divider" style={{
      padding: "12px 16px",
      borderBottom: `1px solid ${branding.border_color || "#e5e7eb"}`,
      color: valueColor || branding.secondary_color || "#1f2937",
      fontSize: "14px",
      fontFamily: monoFont,
      textAlign: "right",
    }}>{value}</td>
  </tr>
);

export const InfoAmount = ({ branding, label, value }: { branding: Branding; label: string; value: string }) => (
  <tr>
    <td className="email-row-label email-amount-bg" style={{
      padding: "12px 16px",
      color: branding.secondary_color || "#6b7280",
      fontSize: "14px",
      fontWeight: 400,
      whiteSpace: "nowrap",
      backgroundColor: branding.highlight_color || "#e5e7eb",
    }}>{label}</td>
    <td className="email-row-value email-amount-bg" style={{
      padding: "12px 16px",
      color: "#000000",
      fontSize: "14px",
      fontFamily: monoFont,
      fontWeight: 700,
      textAlign: "right",
      backgroundColor: branding.highlight_color || "#e5e7eb",
    }}>{value}</td>
  </tr>
);
