"""Module with config schema to validate it"""

import trafaret as tr

CONFIG_SCHEMA = tr.Dict({
    tr.Key('general'):
        tr.Dict({
            'project_name': tr.String(),
            'config': tr.String(),
            'processes': tr.Int(),
        }),
    tr.Key('paths'):
        tr.Dict({
            'project_folder': tr.String(),
            'fasta_input_folder': tr.String(),
            'extract_output': tr.String(),
            'prodigal_output': tr.String(),
            'hmmsearch_output': tr.String(),
            'align_output': tr.String(allow_blank=True),
        }),
    tr.Key('prefixes'):
        tr.Dict({
            'nuc_prefix': tr.String(),
            'pro_prefix': tr.String(),
            'align_prefix': tr.String(allow_blank=True),
        }),
    tr.Key('tools'):
        tr.Dict({
            'prodigal_like_tool': tr.String(),
            'hmmsearch_like_tool': tr.String(),
            'align_tool': tr.String(),
        }),
    tr.Key('biological'):
        tr.Dict({
            'prodigal_translation_table': tr.Int(),
            'ubcg_gene': tr.List(tr.String),
            'hmm_base': tr.String(),
        }),
})
