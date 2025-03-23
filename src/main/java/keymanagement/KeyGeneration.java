package keymanagement;

import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.HashMap;
import java.util.Map;

public class KeyGeneration {

    private static final BigInteger PRIME = new BigInteger("208351617316091241234326746312124448251235562226470491514186331217050270460481");

    public static Map<Integer, BigInteger> generateShares(BigInteger secret, int totalShares, int threshold) {
        SecureRandom random = new SecureRandom();
        BigInteger[] coefficients = new BigInteger[threshold - 1];
        for (int i = 0; i < threshold - 1; i++) {
            coefficients[i] = new BigInteger(PRIME.bitLength(), random).mod(PRIME);
        }

        Map<Integer, BigInteger> shares = new HashMap<>();
        for (int x = 1; x <= totalShares; x++) {
            BigInteger y = secret;
            for (int i = 0; i < threshold - 1; i++) {
                y = y.add(coefficients[i].multiply(BigInteger.valueOf(x).pow(i + 1))).mod(PRIME);
            }
            shares.put(x, y);
        }
        return shares;
    }

    public static BigInteger reconstructSecret(Map<Integer, BigInteger> shares) {
        BigInteger secret = BigInteger.ZERO;
        for (Map.Entry<Integer, BigInteger> entry : shares.entrySet()) {
            BigInteger numerator = BigInteger.ONE;
            BigInteger denominator = BigInteger.ONE;
            for (Map.Entry<Integer, BigInteger> otherEntry : shares.entrySet()) {
                if (!entry.getKey().equals(otherEntry.getKey())) {
                    numerator = numerator.multiply(BigInteger.valueOf(-otherEntry.getKey())).mod(PRIME);
                    denominator = denominator.multiply(BigInteger.valueOf(entry.getKey() - otherEntry.getKey())).mod(PRIME);
                }
            }
            BigInteger term = entry.getValue().multiply(numerator).multiply(denominator.modInverse(PRIME)).mod(PRIME);
            secret = secret.add(term).mod(PRIME);
        }
        return secret;
    }
}