package signing;

import event.NostrEvent;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Map;
import java.util.logging.Logger;

public class FrostThresholdSignature {

    private static final Logger logger = Logger.getLogger(FrostThresholdSignature.class.getName());
    private static final BigInteger PRIME = new BigInteger("208351617316091241234326746312124448251235562226470491514186331217050270460481");

    // Generate a nonce for signing
    public static BigInteger generateNonce() {
        SecureRandom random = new SecureRandom();
        return new BigInteger(PRIME.bitLength(), random).mod(PRIME);
    }

    // Generate a partial signature for an event
    public static BigInteger generatePartialSignature(NostrEvent event, BigInteger secretShare, BigInteger nonce) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = digest.digest(event.getContentHash().getBytes(StandardCharsets.UTF_8));
        BigInteger hash = new BigInteger(1, hashBytes);

        // Partial signature: s_i = hash * secretShare + nonce mod PRIME
        BigInteger partialSignature = hash.multiply(secretShare).add(nonce).mod(PRIME);
        logger.info("Generated partial signature for event: " + event.getId());
        return partialSignature;
    }

    // Aggregate partial signatures into a final signature
    public static BigInteger aggregateSignatures(Map<Integer, BigInteger> partialSignatures, Map<Integer, BigInteger> shares) {
        BigInteger finalSignature = BigInteger.ZERO;
        for (Map.Entry<Integer, BigInteger> entry : partialSignatures.entrySet()) {
            int x = entry.getKey();
            BigInteger s_i = entry.getValue();
            BigInteger lagrangeCoefficient = calculateLagrangeCoefficient(x, shares);
            finalSignature = finalSignature.add(s_i.multiply(lagrangeCoefficient)).mod(PRIME);
        }
        logger.info("Aggregated partial signatures into final signature.");
        return finalSignature;
    }

    // Calculate the Lagrange coefficient for a given share
    private static BigInteger calculateLagrangeCoefficient(int x, Map<Integer, BigInteger> shares) {
        BigInteger numerator = BigInteger.ONE;
        BigInteger denominator = BigInteger.ONE;
        for (Map.Entry<Integer, BigInteger> otherEntry : shares.entrySet()) {
            if (x != otherEntry.getKey()) {
                numerator = numerator.multiply(BigInteger.valueOf(-otherEntry.getKey())).mod(PRIME);
                denominator = denominator.multiply(BigInteger.valueOf(x - otherEntry.getKey())).mod(PRIME);
            }
        }
        return numerator.multiply(denominator.modInverse(PRIME)).mod(PRIME);
    }
}