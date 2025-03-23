package event;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.logging.Logger;

public class NostrEvent {

    private static final Logger logger = Logger.getLogger(NostrEvent.class.getName());

    private final String id;
    private final String pubkey;
    private final long created_at;
    private final String content;
    private final String contentHash;

    public NostrEvent(String pubkey, String content) {
        this.pubkey = pubkey;
        this.content = content;
        this.created_at = Instant.now().getEpochSecond();
        this.contentHash = calculateContentHash(content);
        this.id = calculateEventId();
        logger.info("Created new Nostr event: " + this);
    }

    public String getId() {
        return id;
    }

    public String getPubkey() {
        return pubkey;
    }

    public long getCreatedAt() {
        return created_at;
    }

    public String getContent() {
        return content;
    }

    public String getContentHash() {
        return contentHash;
    }

    private String calculateContentHash(String content) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashBytes = digest.digest(content.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(hashBytes);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    private String calculateEventId() {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            String serializedEvent = String.format("%s%d%s%s", pubkey, created_at, contentHash, content);
            byte[] hashBytes = digest.digest(serializedEvent.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(hashBytes);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    private String bytesToHex(byte[] bytes) {
        StringBuilder hexString = new StringBuilder();
        for (byte b : bytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }
        return hexString.toString();
    }

    @Override
    public String toString() {
        return String.format(
                "NostrEvent{id='%s', pubkey='%s', created_at=%d, content='%s', contentHash='%s'}",
                id, pubkey, created_at, content, contentHash
        );
    }
}