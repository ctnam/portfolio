/**
 * DOC
 * initiateToRecipient: an initiator identifies the recipient
 */

interface Initiator<T extends Player> {
    T initiateToRecipient (T recipient);
}

