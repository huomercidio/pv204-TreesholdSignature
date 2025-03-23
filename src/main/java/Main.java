import device.Device;
import event.NostrEvent;
import keymanagement.KeyGeneration;
import keymanagement.KeyManager;
import signing.AutomaticSigner;
import signing.EventValidator;
import signing.FrostThresholdSignature;

import java.math.BigInteger;
import java.security.KeyPair;
import java.security.PublicKey;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

public class Main {

    private static final Logger logger = Logger.getLogger(Main.class.getName());

    public static void main(String[] args) {
        try {
            // Step 1: Generate a secret and shares
            BigInteger secret = new BigInteger("123456789"); // Example secret
            int totalShares = 5;
            int threshold = 3;

            // Step 2: Generate a key pair
            KeyPair keyPair = KeyManager.generateKeyPair();
            logger.info("Generated key pair: " + keyPair);

            // Step 3: Create devices and generate shares
            Device device1 = new Device(secret, totalShares, threshold);
            Device device2 = new Device(secret, totalShares, threshold);
            Device device3 = new Device(secret, totalShares, threshold);

            // Step 4: Create a Nostr event
            PublicKey publicKey = keyPair.getPublic();
            String pubkey = KeyManager.getPublicKeyFromBytes(publicKey.getEncoded()).toString();
            NostrEvent event = new NostrEvent(pubkey, "Hello, Nostr!");

            // Log event details
            logger.info("Created Event: " + event);
            logger.info("Event ID: " + event.getId());
            logger.info("Event Public Key: " + event.getPubkey());
            logger.info("Event Timestamp: " + event.getCreatedAt());
            logger.info("Event Content: " + event.getContent());
            logger.info("Event Content Hash: " + event.getContentHash());

            // Step 5: Generate partial signatures
            Map<Integer, BigInteger> partialSignatures = new HashMap<>();
            partialSignatures.put(1, device1.generatePartialSignature(event));
            partialSignatures.put(2, device2.generatePartialSignature(event));
            partialSignatures.put(3, device3.generatePartialSignature(event));

            // Step 6: Aggregate partial signatures
            BigInteger finalSignature = FrostThresholdSignature.aggregateSignatures(partialSignatures, device1.getShares());
            logger.info("Final Signature: " + finalSignature.toString(16));

            // Step 7: Validate the event
            boolean isValid = EventValidator.validateEvent(event, finalSignature.toByteArray(), publicKey);
            logger.info("Event validation result: " + isValid);
        } catch (Exception e) {
            logger.severe("An error occurred: " + e.getMessage());
        }
    }
}