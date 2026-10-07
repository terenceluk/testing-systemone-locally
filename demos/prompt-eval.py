"""Scores different ways of describing a Space Invaders board to a decision model.

Run it with a decision model loaded in llama serve:

    python prompt-eval.py

It builds 98 board situations, each with a known sensible move, and asks the
model the same question in several different wordings.
"""
import json
import urllib.request

# 127.0.0.1 and not localhost, because on Windows Python tries IPv6 first and
# waits about two seconds per request before falling back.
URL = "http://127.0.0.1:8080/v1/systemone"


def ask(state, question):
    body = json.dumps({"state": state, "questions": {"q": question}}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["answers"]["q"]


def build_cases():
    cases = []
    for bomb in ["none", "over_left_clear", "over_right_clear", "near_left", "near_right"]:
        for target in ["left_short", "left_far", "right_short", "right_far", "above"]:
            for ready in [True, False]:
                for wall in ["none", "left", "right"]:
                    if wall == "left" and (target.startswith("left") or bomb == "over_left_clear"):
                        continue
                    if wall == "right" and (target.startswith("right") or bomb == "over_right_clear"):
                        continue
                    if bomb.startswith("over"):
                        act = "left" if "left" in bomb else "right"
                    elif target == "above":
                        act = "fire"
                    elif bomb.startswith("near") and bomb.split("_")[1] == target.split("_")[0]:
                        act = "wait"
                    else:
                        act = target.split("_")[0]
                    cases.append({"bomb": bomb, "target": target, "ready": ready, "wall": wall, "act": act})
    return cases


def bomb_side(c):
    return "left" if "left" in c["bomb"] else "right"


def full_description(c):
    out = []
    if c["bomb"].startswith("over"):
        out.append("A bomb is falling directly above the cannon. The %s side is clear." % bomb_side(c))
    elif c["bomb"].startswith("near"):
        out.append("A bomb is falling close by on the %s." % bomb_side(c))
    else:
        out.append("No bombs are near the cannon.")
    if c["target"] == "above":
        out.append("An invader is directly above the cannon.")
    else:
        side, dist = c["target"].split("_")
        out.append("The nearest invader is %s to the %s." % ("far" if dist == "far" else "a short way", side))
    out.append("The cannon is ready to fire." if c["ready"] else "A shot is already in the air.")
    if c["wall"] != "none":
        out.append("The cannon is at the %s wall." % c["wall"])
    return " ".join(out)


def two_facts(c):
    if c["bomb"].startswith("over"):
        first = "A bomb is directly overhead. The only clear side is the %s." % bomb_side(c)
    elif c["bomb"].startswith("near"):
        first = "A bomb is falling close by on the %s." % bomb_side(c)
    else:
        first = "No bombs are nearby."
    second = "An invader is directly overhead." if c["target"] == "above" else \
        "The nearest invader is to the %s." % c["target"].split("_")[0]
    return first + " " + second


def one_fact(c):
    if c["bomb"].startswith("over"):
        return "A bomb is directly overhead. The only clear side is the %s." % bomb_side(c)
    if c["act"] == "fire":
        return "An invader is directly overhead."
    if c["act"] == "wait":
        return "A bomb is blocking the way to the nearest invader."
    return "The nearest invader is to the %s." % c["target"].split("_")[0]


LONG = {
    "left": "Move left, because the clear side is the left, or the nearest invader is to the left and no bomb is in the way",
    "right": "Move right, because the clear side is the right, or the nearest invader is to the right and no bomb is in the way",
    "stay": "Stay still, because an invader is directly above the cannon and no bomb is overhead",
}
SHORT = {
    "left": "the clear side or the nearest invader is to the left",
    "right": "the clear side or the nearest invader is to the right",
    "stay": "an invader is directly overhead, or the way is blocked",
}
ACTIONS = {
    "left": "move left, the clear side or the nearest invader is to the left",
    "right": "move right, the clear side or the nearest invader is to the right",
    "fire": "shoot, an invader is directly overhead",
    "wait": "hold still, a bomb is blocking the way",
}
FACTS = {
    "left": "the clear side or the nearest invader is to the left",
    "right": "the clear side or the nearest invader is to the right",
    "fire": "an invader is directly overhead",
    "wait": "a bomb is blocking the way",
}
LONG_Q = ("Which way should the cannon move next? Getting out from under a falling bomb comes first, "
          "and lining up under the nearest invader comes second.")


def score(name, cases, state_fn, instructions, criteria):
    three = "stay" in criteria
    right = 0
    picks = {}
    conf_right = conf_wrong = 0.0
    for c in cases:
        want = "stay" if three and c["act"] in ("fire", "wait") else c["act"]
        a = ask(state_fn(c), {"type": "choice", "instructions": instructions, "criteria": criteria})
        picks[a["choice"]] = picks.get(a["choice"], 0) + 1
        if a["choice"] == want:
            right += 1
            conf_right += a["confidence"]
        else:
            conf_wrong += a["confidence"]
    n = len(cases)
    print("%-52s %3d of %d  %3.0f%%  confidence when right %.2f, when wrong %.2f  picks %s" % (
        name, right, n, 100 * right / n, conf_right / max(1, right), conf_wrong / max(1, n - right), picks))


def main():
    cases = build_cases()
    print(len(cases), "situations")
    score("1. Full description, long criteria", cases, full_description, LONG_Q, LONG)
    score("2. Full description, short criteria", cases, full_description, "Which way should the cannon move?", SHORT)
    score("3. Two facts, short criteria", cases, two_facts, "Which way should the cannon move?", SHORT)
    score("4. One fact, short criteria", cases, one_fact, "Which way should the cannon move?", SHORT)
    score("5. One fact, four options worded as actions", cases, one_fact, "What should the cannon do?", ACTIONS)
    score("6. The same four options in reverse order", cases, one_fact, "What should the cannon do?",
          dict(reversed(list(ACTIONS.items()))))
    score("7. One fact, four options worded as facts", cases, one_fact, "What should the cannon do?", FACTS)
    score("8. The same four options in reverse order", cases, one_fact, "What should the cannon do?",
          dict(reversed(list(FACTS.items()))))


if __name__ == "__main__":
    main()
