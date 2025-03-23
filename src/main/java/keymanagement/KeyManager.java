package keymanagement;

import java.math.BigInteger;
import java.security.*;
import java.security.spec.*;

import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.jce.spec.ECParameterSpec;
import org.bouncycastle.math.ec.ECCurve;
import org.bouncycastle.math.ec.ECPoint;
import org.bouncycastle.math.ec.custom.sec.SecP256R1Curve;

import java.util.logging.Logger;

public class KeyManager {

    private static final Logger logger = Logger.getLogger(KeyManager.class.getName());
    private static final String EC_CURVE_NAME = "secp256r1"; // Elliptic curve name

    static {
        Security.addProvider(new BouncyCastleProvider()); // Register BouncyCastle provider
    }

    /**
     * Generates a new EC key pair using the secp256r1 curve.
     *
     * @return A KeyPair containing the public and private keys.
     * @throws NoSuchAlgorithmException If the EC algorithm is not available.
     * @throws InvalidAlgorithmParameterException If the curve parameters are invalid.
     */
    public static KeyPair generateKeyPair() throws NoSuchAlgorithmException, InvalidAlgorithmParameterException {
        try {
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("EC", "BC"); // Use BouncyCastle provider
            ECGenParameterSpec ecSpec = new ECGenParameterSpec(EC_CURVE_NAME); // Use secp256r1 curve
            keyPairGenerator.initialize(ecSpec, new SecureRandom());
            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            logger.info("Generated EC key pair using curve: " + EC_CURVE_NAME);
            return keyPair;
        } catch (NoSuchProviderException e) {
            logger.severe("BouncyCastle provider not available: " + e.getMessage());
            throw new NoSuchAlgorithmException("BouncyCastle provider not available", e);
        }
    }

    /**
     * Derives the public key from a given private key.
     *
     * @param privateKey The private key to derive the public key from.
     * @return The derived public key.
     * @throws IllegalArgumentException If the private key is not an EC private key.
     * @throws NoSuchAlgorithmException If the EC algorithm is not available.
     * @throws InvalidKeySpecException If the key specification is invalid.
     */
    @SuppressWarnings("unused")  public static PublicKey getPublicKeyFromPrivateKey(PrivateKey privateKey) throws NoSuchAlgorithmException, InvalidKeySpecException {
        if (!(privateKey instanceof java.security.interfaces.ECPrivateKey)) {
            throw new IllegalArgumentException("Private key must be an EC private key.");
        }

        java.security.interfaces.ECPrivateKey ecPrivateKey = (java.security.interfaces.ECPrivateKey) privateKey;
        ECParameterSpec bcEcSpec = convertToBouncyCastleSpec(ecPrivateKey.getParams());

        // Multiply base point by private key scalar
        ECPoint publicKeyPoint = multiplyBasePoint(bcEcSpec, ecPrivateKey.getS());

        ECPublicKeySpec publicKeySpec = new ECPublicKeySpec(
                new java.security.spec.ECPoint(
                        publicKeyPoint.getAffineXCoord().toBigInteger(),
                        publicKeyPoint.getAffineYCoord().toBigInteger()
                ),
                ecPrivateKey.getParams()
        );

        try {
            KeyFactory keyFactory = KeyFactory.getInstance("EC", "BC"); // Use BouncyCastle provider
            PublicKey publicKey = keyFactory.generatePublic(publicKeySpec);
            logger.info("Derived public key from private key.");
            return publicKey;
        } catch (NoSuchProviderException e) {
            logger.severe("BouncyCastle provider not available: " + e.getMessage());
            throw new NoSuchAlgorithmException("BouncyCastle provider not available", e);
        }
    }

    /**
     * Reconstructs a public key from its encoded bytes.
     *
     * @param encodedKey The encoded public key bytes.
     * @return The reconstructed public key.
     * @throws NoSuchAlgorithmException If the EC algorithm is not available.
     * @throws InvalidKeySpecException If the key specification is invalid.
     */
    public static PublicKey getPublicKeyFromBytes(byte[] encodedKey) throws NoSuchAlgorithmException, InvalidKeySpecException {
        if (encodedKey == null || encodedKey.length == 0) {
            throw new IllegalArgumentException("Encoded key cannot be null or empty.");
        }
        try {
            KeyFactory keyFactory = KeyFactory.getInstance("EC", "BC"); // Use BouncyCastle provider
            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(encodedKey);
            PublicKey publicKey = keyFactory.generatePublic(keySpec);
            logger.info("Reconstructed public key from encoded bytes.");
            return publicKey;
        } catch (NoSuchProviderException e) {
            logger.severe("BouncyCastle provider not available: " + e.getMessage());
            throw new NoSuchAlgorithmException("BouncyCastle provider not available", e);
        }
    }

    /**
     * Converts Java ECParameterSpec to Bouncy Castle ECParameterSpec.
     *
     * @param ecParams Java ECParameterSpec
     * @return Equivalent Bouncy Castle ECParameterSpec
     */
    private static ECParameterSpec convertToBouncyCastleSpec(java.security.spec.ECParameterSpec ecParams) {
        ECCurve curve = new SecP256R1Curve(); // secp256r1 curve
        ECPoint generator = curve.createPoint(ecParams.getGenerator().getAffineX(), ecParams.getGenerator().getAffineY());

        return new ECParameterSpec(
                curve,
                generator,
                ecParams.getOrder(),
                BigInteger.valueOf(ecParams.getCofactor())
        );
    }

    /**
     * Multiplies the base point of the elliptic curve by a scalar (private key).
     *
     * @param ecSpec The elliptic curve parameters.
     * @param scalar The scalar (private key) to multiply by.
     * @return The resulting EC point (public key).
     */
    private static ECPoint multiplyBasePoint(ECParameterSpec ecSpec, BigInteger scalar) {
        ECPoint basePoint = ecSpec.getG(); // Generator point
        ECPoint publicKeyPoint = basePoint.multiply(scalar);
        logger.info("Multiplied base point by scalar to derive public key point.");
        return publicKeyPoint;
    }
}
