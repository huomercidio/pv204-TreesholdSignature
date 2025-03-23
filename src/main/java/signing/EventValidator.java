package signing;

import event.NostrEvent;

import java.nio.charset.StandardCharsets;
import java.security.*;

public class EventValidator {

    public static boolean validateEvent(NostrEvent event, byte[] signature, PublicKey publicKey) throws NoSuchAlgorithmException, InvalidKeyException, SignatureException {
        Signature sig = Signature.getInstance("SHA256withECDSA");
        sig.initVerify(publicKey);
        sig.update(event.getContentHash().getBytes(StandardCharsets.UTF_8));
        return sig.verify(signature);
    }
}