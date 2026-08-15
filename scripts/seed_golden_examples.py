from src.database import get_session, GoldenExample, create_tables
from src.rag.embeddings import generate_embedding

GOLDEN_EXAMPLES_DATA = [
    {
        "user_query": "I was charged twice for my subscription this month. Please fix this.",
        "perfect_response": "I'm sorry about the duplicate charge! I've flagged this for our billing team to review and process a refund for the extra charge. You should see the correction reflected within 3–5 business days.",
        "category": "billing",
    },
    {
        "user_query": "why did u charge me $50?? i only signed up for the $30 plan",
        "perfect_response": "I understand the confusion. The difference may be due to taxes, add-ons, or a plan mismatch at signup. I've noted this discrepancy and our billing team will review your account and contact you with a full breakdown.",
        "category": "billing",
    },
    {
        "user_query": "My invoice shows a charge I don't recognize from last Tuesday.",
        "perfect_response": "I'll flag that unrecognized charge for investigation. Could you confirm the exact amount and the date it appeared? Our billing team will review and follow up with you directly.",
        "category": "billing",
    },
    {
        "user_query": "I cancelled my subscription last week but still got charged for this month.",
        "perfect_response": "I'm sorry about that. If the cancellation was processed after the billing cycle started, a charge may still have gone through. Our billing team will review your cancellation date and issue a refund if applicable.",
        "category": "billing",
    },
    {
        "user_query": "how do i get a refund for my last order? it arrived broken",
        "perfect_response": "I'm sorry your order arrived damaged! To initiate a refund, please provide your order number and a photo of the damage if possible. Our team will process the refund once the issue is verified.",
        "category": "billing",
    },
    {
        "user_query": "my payment failed but i can see the money was deducted from my bank",
        "perfect_response": "If your bank shows a deduction but the payment failed on our end, it's likely a pending authorization that will be released within 3–7 business days. If the hold persists beyond that, please contact your bank and share a screenshot with our billing team.",
        "category": "billing",
    },
    {
        "user_query": "The app says my subscription is active but I got charged again when I tried to upgrade.",
        "perfect_response": "It sounds like you may have been billed for both plans during the upgrade. Our billing team will review the transaction and ensure you're only charged for your current plan. Any duplicate charges will be refunded.",
        "category": "billing",
    },
    {
        "user_query": "Can I get an official receipt for my payment last month? I need it for expense reporting.",
        "perfect_response": "Absolutely! You can download your receipts from the Billing section in your account settings. If you need a formal invoice with company details, please let us know and we can generate one for you.",
        "category": "billing",
    },
    {
        "user_query": "i tried to add a new payment method and now im being charged to two cards",
        "perfect_response": "That doesn't sound right. Please check your Billing settings to confirm which payment method is set as primary. If charges went to both cards, our billing team will investigate and refund the duplicate charge.",
        "category": "billing",
    },
    {
        "user_query": "My free trial ended and you immediately charged me without any warning.",
        "perfect_response": "Free trials automatically convert to paid subscriptions at the end of the trial period, which is noted in the trial terms. If you weren't aware of the charge timing, please contact our billing team — they'll review your case.",
        "category": "billing",
    },
    {
        "user_query": "Is there any way to get a partial refund? I barely used the service this month.",
        "perfect_response": "Partial refunds are handled case by case by our billing team. Please reach out with your account details and the reason for the request, and they will review what can be done.",
        "category": "billing",
    },
    {
        "user_query": "I updated my credit card but I'm still seeing the old one listed and got charged to it",
        "perfect_response": "If the charge went to your old card despite updating, the new card may not have saved correctly. Please re-enter your card details in Billing settings and ensure you press Save. If the old card was charged, our billing team will assist with reversing it.",
        "category": "billing",
    },
    {
        "user_query": "do you guys charge in USD or EUR? my bank is converting at a bad rate",
        "perfect_response": "All charges are processed in USD by default. Currency conversion rates are determined by your bank or card provider. Unfortunately, we don't have control over their exchange rates, but your bank may offer options to reduce conversion fees.",
        "category": "billing",
    },
    {
        "user_query": "I signed up for annual billing but I'm being charged every month instead",
        "perfect_response": "That sounds like a plan selection issue at signup. I'll have our billing team verify your subscription settings and correct the billing cycle if needed. If any overcharges occurred, they will be refunded.",
        "category": "billing",
    },
    {
        "user_query": "why is my bill higher than last month? i didnt change anything",
        "perfect_response": "Price changes, tax adjustments, or usage-based billing could cause variations month to month. Your invoice in the Billing section will show a full itemized breakdown. If something still looks off, our billing team can review it with you.",
        "category": "billing",
    },
    {
        "user_query": "I need to dispute a charge from three months ago. It was never authorized.",
        "perfect_response": "I understand. Please provide the charge date and amount so our billing team can investigate. Note that most banks also allow direct chargebacks for unauthorized transactions if needed.",
        "category": "billing",
    },
    {
        "user_query": "my promo code didn't apply at checkout but I was still charged full price",
        "perfect_response": "I'm sorry the promo code didn't apply correctly. Please share the code you used and your order details, and our billing team will verify its validity and apply the discount or refund the difference.",
        "category": "billing",
    },
    {
        "user_query": "the app crashes whenever i try to open it on my android phone",
        "perfect_response": "I'm sorry you're experiencing crashes! Please try clearing the app cache, ensuring you have the latest version installed, and restarting your device. If it still crashes, please share your Android version and device model so our team can investigate.",
        "category": "technical",
    },
    {
        "user_query": "I keep getting a 500 error when I try to submit my order",
        "perfect_response": "A 500 error indicates a server-side issue on our end. Please try again in a few minutes, and if the problem persists, share the exact URL and steps you took so our technical team can investigate.",
        "category": "technical",
    },
    {
        "user_query": "the dashboard just shows a blank white screen after I log in",
        "perfect_response": "A blank screen after login is often caused by cached data or a browser extension conflict. Please try opening the dashboard in a private/incognito window or a different browser. If the issue persists, please let us know your browser version.",
        "category": "technical",
    },
    {
        "user_query": "notifications stopped working on my account, I'm not getting any emails",
        "perfect_response": "Please check your notification preferences in your Account Settings to confirm email notifications are enabled. Also check your spam folder. If settings look correct and emails are still not arriving, our technical team can investigate your notification delivery.",
        "category": "technical",
    },
    {
        "user_query": "the search bar in the app doesn't return any results no matter what I type",
        "perfect_response": "A non-functional search bar is likely a bug. Please try refreshing the page or reinstalling the app. If the issue persists, please note your app version and operating system so our team can identify and fix the root cause.",
        "category": "technical",
    },
    {
        "user_query": "API integration keeps returning 401 unauthorized even though my key is correct",
        "perfect_response": "A 401 error usually indicates an authentication issue. Please confirm your API key is active and that it's being sent in the correct Authorization header format. If the key is valid and the error persists, please share the request structure (without the key) so our team can assist.",
        "category": "technical",
    },
    {
        "user_query": "images are not loading in the product catalog. everything else works fine",
        "perfect_response": "Image loading issues are often caused by a CDN or caching problem on our side. Please try a hard refresh (Ctrl+Shift+R) and clearing your browser cache. If images are still missing, please let us know which browser and network you're using.",
        "category": "technical",
    },
    {
        "user_query": "the app is super slow and takes forever to load anything",
        "perfect_response": "Performance issues can stem from your network speed, device resources, or a temporary server load on our side. Please check your internet connection, close other background apps, and try again. If slowness continues, share your device specs so our team can investigate.",
        "category": "technical",
    },
    {
        "user_query": "File upload keeps failing at 80% every single time. I've tried three times.",
        "perfect_response": "Repeated upload failures at a fixed percentage often indicate a file size limit, timeout, or a connection interruption. Please check if your file exceeds our maximum upload size. If it's within limits, try on a stable connection or a different browser.",
        "category": "technical",
    },
    {
        "user_query": "The export to CSV button does nothing when I click it",
        "perfect_response": "A non-responsive export button can be caused by a browser extension blocking the download or a temporary bug. Please try in an incognito window or a different browser. If the issue persists, share the browser and OS version so our team can reproduce it.",
        "category": "technical",
    },
    {
        "user_query": "getting 'connection timed out' errors every few minutes while using the platform",
        "perfect_response": "Intermittent timeout errors may be caused by network instability or temporary server issues. Please check your connection and try a different network if possible. If timeouts are recurring consistently, please note the time they occur so our team can cross-check server logs.",
        "category": "technical",
    },
    {
        "user_query": "The two-factor auth code isn't being delivered to my phone anymore",
        "perfect_response": "2FA delivery issues are often caused by carrier delays or a changed phone number. Please check your spam SMS folder and ensure your phone number in Account Settings is current. If you're locked out, our support team can assist you with account recovery.",
        "category": "technical",
    },
    {
        "user_query": "dark mode option disappeared from settings after the last update",
        "perfect_response": "It sounds like a UI regression may have occurred in the latest update. Please try logging out and back in to refresh your settings. If dark mode is still missing, please share your app version and platform so our team can investigate.",
        "category": "technical",
    },
    {
        "user_query": "my data isn't syncing between the mobile app and the web version",
        "perfect_response": "Sync issues are typically resolved by logging out and back in on both platforms to force a refresh. If data is still out of sync after that, please let us know which platform shows the correct data and which is lagging behind.",
        "category": "technical",
    },
    {
        "user_query": "the checkout button on your website doesn't work in Safari",
        "perfect_response": "Safari compatibility issues can sometimes be caused by browser privacy settings or extensions blocking scripts. Please try disabling any browser extensions and ensure Safari is up to date. Alternatively, Chrome or Firefox may work as a temporary workaround while our team investigates.",
        "category": "technical",
    },
    {
        "user_query": "I'm getting a certificate error when trying to access the app. Says the site is not secure.",
        "perfect_response": "SSL certificate errors can sometimes appear during certificate renewal or due to incorrect system date/time settings on your device. Please check your device's date and time settings first. If the error persists, please share the exact error message so our team can investigate.",
        "category": "technical",
    },
    {
        "user_query": "Graph charts on the analytics page stopped rendering, just showing blank boxes",
        "perfect_response": "Blank chart rendering is usually caused by a JavaScript error or a browser incompatibility. Please try a hard refresh and check the browser console for errors if you're technical. Otherwise, share your browser version and OS so our team can reproduce and fix the issue.",
        "category": "technical",
    },
    {
        "user_query": "i forgot my password and the reset email never arrives",
        "perfect_response": "Password reset emails can sometimes land in spam or be delayed. Please check your spam/junk folder and ensure you entered the correct email address. If the email still doesn't arrive after a few minutes, our support team can help you reset your account manually.",
        "category": "account",
    },
    {
        "user_query": "how do i change my email address? I can't find the option anywhere",
        "perfect_response": "You can update your email address by going to Account Settings > Personal Information > Email. You'll need to verify the new email address before the change takes effect.",
        "category": "account",
    },
    {
        "user_query": "I think my account got hacked. There are logins I don't recognize.",
        "perfect_response": "Please change your password immediately and enable two-factor authentication in your security settings. Review the active sessions list in your account and revoke any sessions you don't recognize. Contact our support team right away if you need further assistance securing your account.",
        "category": "account",
    },
    {
        "user_query": "I want to permanently delete my account. How do I do that?",
        "perfect_response": "You can request account deletion from Account Settings > Privacy > Delete Account. Please note that deletion is permanent and all your data will be removed. If you need help finding the option, our support team can guide you through the process.",
        "category": "account",
    },
    {
        "user_query": "I set up 2FA but now I lost my authenticator app and can't log in",
        "perfect_response": "I understand this is urgent. Please use one of your backup codes if you saved them during 2FA setup. If you don't have them, contact our support team with proof of identity to initiate account recovery.",
        "category": "account",
    },
    {
        "user_query": "can i change my username? i made a typo when i signed up",
        "perfect_response": "Yes, you can update your username from Account Settings > Profile. If the option isn't available or the change doesn't save, please contact our support team and they can update it manually.",
        "category": "account",
    },
    {
        "user_query": "my account is locked and i dont know why. I never violated any rules",
        "perfect_response": "Account locks can sometimes be triggered automatically by suspicious activity or a failed login attempt threshold. Please contact our support team with your account email, and they will review the lock reason and help restore access.",
        "category": "account",
    },
    {
        "user_query": "I got a security alert email about a login from a different country but it was me",
        "perfect_response": "If the login was you, no action is needed. However, it's a good practice to confirm your active sessions in Account Settings > Security and revoke any you don't recognize. You can also add a trusted device list to reduce future alerts.",
        "category": "account",
    },
    {
        "user_query": "how can i download all my personal data from your platform?",
        "perfect_response": "You can request a full data export from Account Settings > Privacy > Export My Data. The export will be prepared and sent to your registered email address, typically within 24–48 hours.",
        "category": "account",
    },
    {
        "user_query": "i want to add a second user to my account so my colleague can access it",
        "perfect_response": "Team or multi-user access depends on your subscription plan. If your plan supports it, you can invite team members from Account Settings > Team Members. If you don't see this option, you may need to upgrade your plan.",
        "category": "account",
    },
    {
        "user_query": "I can no longer access my old email address. How do I update my login email?",
        "perfect_response": "Since you no longer have access to your registered email, our support team will need to verify your identity before making changes. Please contact us with any identifying information such as your name, phone number, or previous billing details.",
        "category": "account",
    },
    {
        "user_query": "how do i disconnect Google login and switch to email/password instead?",
        "perfect_response": "You can manage your connected login methods from Account Settings > Security > Connected Accounts. Disconnect Google there and then set a password using the 'Set Password' option. If you run into issues, our support team can assist.",
        "category": "account",
    },
    {
        "user_query": "my profile picture won't update. I upload it and it just reverts back",
        "perfect_response": "Profile picture update issues are often caused by file size or format restrictions. Please ensure your image is under 5MB and is in JPG or PNG format. If the problem continues after that, try a different browser or clear your cache.",
        "category": "account",
    },
    {
        "user_query": "I need to transfer my account to a different email because I'm changing companies",
        "perfect_response": "Account email transfers require identity verification. Please contact our support team with your current and new email addresses along with proof of ownership, and they will assist you with the transition.",
        "category": "account",
    },
    {
        "user_query": "why does it keep logging me out every time i close the browser?",
        "perfect_response": "This is likely caused by your session settings or browser privacy mode. Please check Account Settings > Security > Session Duration and ensure 'Keep me logged in' is enabled. Also confirm you're not using private/incognito mode, which clears sessions on close.",
        "category": "account",
    },
    {
        "user_query": "I want to change my notification preferences but the page won't save my settings",
        "perfect_response": "If your notification preferences aren't saving, try clearing your browser cache and trying again. If the issue persists in multiple browsers, please report it to our technical team as it may be a bug affecting the settings save functionality.",
        "category": "account",
    },
]


def seed_golden_examples() -> None:
    """Embeds and inserts all golden examples into the golden_examples table."""
    session = get_session()
    try:
        existing_count = session.query(GoldenExample).count()
        if existing_count > 0:
            print(f"Skipping seed: {existing_count} golden examples already exist in the database.")
            return

        print(f"Seeding {len(GOLDEN_EXAMPLES_DATA)} golden examples...")
        inserted = 0

        for i, item in enumerate(GOLDEN_EXAMPLES_DATA, start=1):
            print(f"  [{i}/{len(GOLDEN_EXAMPLES_DATA)}] Embedding: {item['user_query'][:60]}...")
            embedding = generate_embedding(item["user_query"])

            example = GoldenExample(
                user_query=item["user_query"],
                perfect_response=item["perfect_response"],
                category=item["category"],
                embedding=embedding if embedding else None,
            )
            session.add(example)
            inserted += 1

        session.commit()
        print(f"\nSeeding completed! {inserted} golden examples inserted.")

    except Exception as e:
        session.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    create_tables()
    seed_golden_examples()
