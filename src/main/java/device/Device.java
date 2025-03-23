package device;

import keymanagement.KeyGeneration;
import signing.FrostThresholdSignature; // Use FrostThresholdSignature instead of ThresholdSignature
import event.NostrEvent; // Import NostrEvent

import java.math.BigInteger;
import java.security.NoSuchAlgorithmException;
import java.util.Map;

public class Device {

    private final Map<Integer, BigInteger> shares;
    private final BigInteger secretShare;

    public Device(BigInteger secret, int totalShares, int threshold) {
        this.shares = KeyGeneration.generateShares(secret, totalShares, threshold);
        this.secretShare = shares.get(1); // Each device holds one share
    }

    public Map<Integer, BigInteger> getShares() {
        return shares;
    }

    public BigInteger getSecretShare() {
        return secretShare;
    }

    public BigInteger generatePartialSignature(NostrEvent event) {
        try {
            BigInteger nonce = FrostThresholdSignature.generateNonce(); // Generate a nonce
            return FrostThresholdSignature.generatePartialSignature(event, secretShare, nonce); // Use FrostThresholdSignature
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }
}